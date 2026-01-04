"""
Simple prototype JIT using llvmlite for *very* restricted numeric functions.
- Compiles functions with integer parameters (one or more) and a single ReturnStatement
  returning expressions made of Numbers, parameter identifiers, and binary ops (+ - * /, comparisons)
- Falls back gracefully when llvmlite isn't available or function is unsupported
"""
import ctypes

try:
    from llvmlite import ir, binding
    _HAS_LLVM = True
    binding.initialize()
    binding.initialize_native_target()
    binding.initialize_native_asmprinter()
except Exception:
    _HAS_LLVM = False


class JITCompileError(RuntimeError):
    pass


def _ensure_target():
    target = binding.Target.from_default_triple()
    target_machine = target.create_target_machine()
    backing_mod = binding.parse_assembly("")
    engine = binding.create_mcjit_compiler(backing_mod, target_machine)
    return engine


def _compile_ir_to_callable(ir_module, fn_name, argcount, is_float=False):
    """Compile IR Module to a native function and return a ctypes callable.
    The returned callable takes `argcount` 64-bit values (ints or doubles) and
    returns the corresponding 64-bit type.
    """
    if not _HAS_LLVM:
        raise JITCompileError("llvmlite not available")

    llvm_ir = str(ir_module)
    mod = binding.parse_assembly(llvm_ir)
    mod.verify()

    target = binding.Target.from_default_triple()
    tm = target.create_target_machine()
    engine = binding.create_mcjit_compiler(mod, tm)
    engine.finalize_object()
    addr = engine.get_function_address(fn_name)
    if addr == 0:
        raise JITCompileError("Failed to get function address")

    # Build CFUNCTYPE signature dynamically
    if is_float:
        ctypes_args = [ctypes.c_double] * argcount
        ret_type = ctypes.c_double
    else:
        ctypes_args = [ctypes.c_longlong] * argcount
        ret_type = ctypes.c_longlong

    cfunc_type = ctypes.CFUNCTYPE(ret_type, *ctypes_args)
    cfunc = cfunc_type(addr)
    return cfunc


def _expr_to_ir(node, builder, func_args, module, is_float=False):
    """Recursively compile limited AST expression nodes to LLVM IR values.
    node: AST node (we expect BinaryExpression, NumberLiteral, Identifier)
    builder: llvmlite.ir.IRBuilder
    func_args: dict mapping parameter name -> llvmlite.ir.Argument
    module: llvmlite.ir.Module used for types/constants
    is_float: whether we should emit floating-point IR (double)
    """
    t = node.type
    # Number literal: choose int or double constant depending on mode
    if t == 'NumberLiteral':
        if is_float:
            return ir.Constant(ir.DoubleType(), float(node.value))
        return ir.Constant(ir.IntType(64), int(node.value))
    if t == 'Identifier':
        # resolve parameter reference
        if node.name in func_args:
            return func_args[node.name]
        raise JITCompileError(f"Unknown identifier '{node.name}' in JIT-compiled function")
    if t == 'BinaryExpression':
        left = _expr_to_ir(node.left, builder, func_args, module, is_float)
        right = _expr_to_ir(node.right, builder, func_args, module, is_float)
        op = node.operator
        if is_float:
            if op == '+':
                return builder.fadd(left, right)
            elif op == '-':
                return builder.fsub(left, right)
            elif op == '*':
                return builder.fmul(left, right)
            elif op == '/':
                return builder.fdiv(left, right)
            elif op in ('<', '>', '<=', '>=', '==', '!='):
                cmp = builder.fcmp_ordered(op, left, right)
                # Convert boolean i1 to double 1.0/0.0
                one = ir.Constant(ir.DoubleType(), 1.0)
                zero = ir.Constant(ir.DoubleType(), 0.0)
                return builder.select(cmp, one, zero)
            else:
                raise JITCompileError(f"Operator {op} not supported in JIT (float)")
        else:
            if op == '+':
                return builder.add(left, right)
            elif op == '-':
                return builder.sub(left, right)
            elif op == '*':
                return builder.mul(left, right)
            elif op == '/':
                # signed division
                return builder.sdiv(left, right)
            elif op == '<':
                cmp = builder.icmp_signed('<', left, right)
                return builder.zext(cmp, ir.IntType(64))
            elif op == '>':
                cmp = builder.icmp_signed('>', left, right)
                return builder.zext(cmp, ir.IntType(64))
            elif op == '<=':
                cmp = builder.icmp_signed('<=', left, right)
                return builder.zext(cmp, ir.IntType(64))
            elif op == '>=':
                cmp = builder.icmp_signed('>=', left, right)
                return builder.zext(cmp, ir.IntType(64))
            elif op == '==':
                cmp = builder.icmp_signed('==', left, right)
                return builder.zext(cmp, ir.IntType(64))
            elif op == '!=':
                cmp = builder.icmp_signed('!=', left, right)
                return builder.zext(cmp, ir.IntType(64))
            else:
                raise JITCompileError(f"Operator {op} not supported in JIT")
    raise JITCompileError(f"Expr type {t} not supported for JIT")

def _detect_float_mode(node):
    """Simple heuristic: returns True if the AST contains float literals or a '/' operator.
    This picks floating-point IR for the whole function when numeric floats or division are used.
    """
    if node is None:
        return False
    t = getattr(node, 'type', None)
    if t == 'NumberLiteral':
        # Parser stores numbers as float; check if non-integer
        try:
            return float(node.value) != int(float(node.value))
        except Exception:
            return False
    if t == 'BinaryExpression':
        if node.operator == '/':
            return True
        return _detect_float_mode(node.left) or _detect_float_mode(node.right)
    if t in ('ReturnStatement', 'ExpressionStatement'):
        return _detect_float_mode(getattr(node, 'value', None) or getattr(node, 'expression', None))
    if t == 'FunctionDeclaration':
        for s in node.body:
            if _detect_float_mode(s):
                return True
        return False
    # Recurse into other composite nodes
    for attr in ('left', 'right', 'arguments', 'value', 'expression', 'body', 'elements', 'pairs'):
        val = getattr(node, attr, None)
        if isinstance(val, list):
            for it in val:
                if _detect_float_mode(it):
                    return True
        elif hasattr(val, 'type'):
            if _detect_float_mode(val):
                return True
    return False


def compile_simple_function(fn_node):
    """Try to compile a FunctionDeclaration AST node to a native callable.
    Returns a Python callable taking ints/doubles and returning ints/doubles, or None if unsupported.
    Supports functions with any number of numeric parameters.
    """
    if not _HAS_LLVM:
        return None

    params = fn_node.params
    print(f"[JIT] compile_simple_function: name={fn_node.name}, params={params}")
    # Simple body: expect a ReturnStatement with an expression
    body = fn_node.body
    if not body:
        print("[JIT] no body")
        return None
    ret_node = None
    for s in body:
        print(f"[JIT] body stmt: {s.type}")
        if s.type == 'ReturnStatement':
            ret_node = s
            break
    if ret_node is None or ret_node.value is None:
        print("[JIT] no return statement or empty return")
        return None

    # Decide numeric mode (float vs int)
    is_float = _detect_float_mode(fn_node)
    print(f"[JIT] float mode={is_float}")

    # Construct LLVM IR
    module = ir.Module(name=f"jit_{fn_node.name}")
    param_ty = ir.DoubleType() if is_float else ir.IntType(64)
    func_ty = ir.FunctionType(param_ty, [param_ty] * len(params))
    fn = ir.Function(module, func_ty, name=fn_node.name)
    block = fn.append_basic_block('entry')
    builder = ir.IRBuilder(block)

    # Map parameter names to IR arguments
    func_args = {}
    for i, pname in enumerate(params):
        arg = fn.args[i]
        arg.name = pname
        func_args[pname] = arg

    try:
        ret_val = _expr_to_ir(ret_node.value, builder, func_args, module, is_float=is_float)
    except JITCompileError as e:
        print(f"[JIT] expression not supported: {e}")
        return None

    # Ensure result is correct return type
    if is_float:
        if not isinstance(ret_val.type, ir.DoubleType):
            # convert integer result to double
            ret_val = builder.sitofp(ret_val, ir.DoubleType())
    else:
        if not isinstance(ret_val.type, ir.IntType) or ret_val.type.width != 64:
            ret_val = builder.sext(ret_val, ir.IntType(64))

    builder.ret(ret_val)

    try:
        cfunc = _compile_ir_to_callable(module, fn_node.name, len(params), is_float=is_float)
    except Exception:
        return None

    def wrapper(*args):
        if len(args) != len(params):
            raise TypeError(f"{fn_node.name} expects {len(params)} arguments, got {len(args)}")
        if is_float:
            return float(cfunc(*[float(a) for a in args]))
        return int(cfunc(*[int(a) for a in args]))

    # Debug: indicate successful JIT compilation
    try:
        print(f"[JIT] compiled function '{fn_node.name}' with {len(params)} args (float={is_float})")
    except Exception:
        pass

    return wrapper
