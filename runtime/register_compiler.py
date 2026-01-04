"""
A small register-based compiler for a subset of Jusu++ used for benchmarking.
Produces a simple register IR: tuples like ('LOADC', dst, const_idx), ('LOAD_NAME', dst, name_idx),
('STORE_NAME', name_idx, src_reg), ('ADD', dst, r1, r2), ('CALL', dst, fn_reg, [arg_regs]), ('RETURN', src_reg)
"""
from compiler.parser import ASTNode

class RegisterCompiler:
    def __init__(self):
        self.consts = []
        self.names = []
        self.instructions = []
        self.next_reg = 0
        self.reg_count = 0

    def _add_const(self, v):
        try:
            idx = self.consts.index(v)
        except ValueError:
            idx = len(self.consts)
            self.consts.append(v)
        return idx

    def _add_name(self, name):
        try:
            idx = self.names.index(name)
        except ValueError:
            idx = len(self.names)
            self.names.append(name)
        return idx

    def new_reg(self):
        r = self.next_reg
        self.next_reg += 1
        self.reg_count = max(self.reg_count, self.next_reg)
        return r

    def compile_program(self, ast):
        # compile top-level statements
        for stmt in ast:
            self.compile_stmt(stmt)
        # top-level return not needed
        return self.instructions, self.consts, self.names, self.reg_count

    def compile_stmt(self, node):
        t = node.type
        if t == 'Assignment':
            r = self.compile_expr(node.value)
            name_idx = self._add_name(node.name)
            self.instructions.append(('STORE_NAME', name_idx, r))
        elif t == 'FunctionDeclaration':
            # compile function into a reg-code object
            compiler = RegisterCompiler()
            # Reserve registers for parameters (params will map to the first N regs)
            for i, p in enumerate(node.params):
                r = compiler.new_reg()
                if not hasattr(compiler, 'param_map'):
                    compiler.param_map = {}
                compiler.param_map[p] = r
            # compile body with parameter map present
            for s in node.body:
                compiler.compile_stmt(s)
            # functions should return via explicit RETURN statements; ensure at least a return of None
            compiler.instructions.append(('RETURN', None))
            code_obj = ('regcode', compiler.instructions, compiler.consts, compiler.names, len(node.params), compiler.reg_count)
            const_idx = self._add_const(code_obj)
            name_idx = self._add_name(node.name)
            dst = self.new_reg()
            self.instructions.append(('LOADC', dst, const_idx))
            self.instructions.append(('STORE_NAME', name_idx, dst))
        elif t == 'ReturnStatement':
            if node.value is None:
                # load None into a register and return it
                dst = self.new_reg()
                const_idx = self._add_const(None)
                self.instructions.append(('LOADC', dst, const_idx))
                self.instructions.append(('RETURN', dst))
            else:
                r = self.compile_expr(node.value)
                self.instructions.append(('RETURN', r))
        elif t == 'ExpressionStatement':
            self.compile_expr(node.expression)
        elif t == 'SayStatement':
            r = self.compile_expr(node.expression)
            print_reg = self.new_reg()
            name_idx = self._add_name('print')
            self.instructions.append(('LOAD_NAME', print_reg, name_idx))
            self.instructions.append(('CALL', None, print_reg, [r]))
        elif t == 'IfStatement':
            # Minimal support: compile condition, then branch, optional else with simple jumps
            cond_reg = self.compile_expr(node.condition)
            then_start = len(self.instructions)
            for s in node.then_branch:
                self.compile_stmt(s)
            if node.else_branch:
                else_start = len(self.instructions)
                for s in node.else_branch:
                    self.compile_stmt(s)
            # This simple compiler does not implement jumps for now; translate only simple ifs
        else:
            raise NotImplementedError(f"Reg compile: stmt {t} not implemented")

    def compile_expr(self, node):
        t = node.type
        if t == 'NumberLiteral' or t == 'StringLiteral' or t == 'BooleanLiteral' or t == 'ArrayLiteral' or t == 'ObjectLiteral':
            val = self._materialize_literal(node)
            idx = self._add_const(val)
            dst = self.new_reg()
            self.instructions.append(('LOADC', dst, idx))
            return dst
        elif t == 'Identifier':
            # If compiling inside a function and identifier is a parameter/local, return its register
            if hasattr(self, 'param_map') and node.name in getattr(self, 'param_map'):
                return self.param_map[node.name]
            name_idx = self._add_name(node.name)
            dst = self.new_reg()
            self.instructions.append(('LOAD_NAME', dst, name_idx))
            return dst
        elif t == 'BinaryExpression':
            r1 = self.compile_expr(node.left)
            r2 = self.compile_expr(node.right)
            dst = self.new_reg()
            op = node.operator
            if op == '+':
                self.instructions.append(('ADD', dst, r1, r2))
            elif op == '-':
                self.instructions.append(('SUB', dst, r1, r2))
            elif op == '*':
                self.instructions.append(('MUL', dst, r1, r2))
            elif op == '/':
                self.instructions.append(('DIV', dst, r1, r2))
            elif op == '<':
                self.instructions.append(('LT', dst, r1, r2))
            elif op == '>':
                self.instructions.append(('GT', dst, r1, r2))
            elif op == '<=':
                self.instructions.append(('LE', dst, r1, r2))
            elif op == '>=':
                self.instructions.append(('GE', dst, r1, r2))
            elif op == '==':
                self.instructions.append(('EQ', dst, r1, r2))
            elif op == '!=':
                self.instructions.append(('NE', dst, r1, r2))
            else:
                raise NotImplementedError(f"Reg compile: binary op {op} not supported")
            return dst
        elif t == 'CallExpression':
            arg_regs = [self.compile_expr(a) for a in node.arguments]
            fn_reg = self.compile_expr(ASTNode('Identifier', name=node.callee))
            dst = self.new_reg()
            self.instructions.append(('CALL', dst, fn_reg, arg_regs))
            return dst
        else:
            raise NotImplementedError(f"Reg compile: expr {t} not implemented")

    def _materialize_literal(self, node):
        if node.type == 'NumberLiteral':
            return node.value
        if node.type == 'StringLiteral':
            return node.value
        if node.type == 'BooleanLiteral':
            return node.value
        if node.type == 'ArrayLiteral':
            return [self._materialize_literal(el) if hasattr(el, 'type') else el for el in node.elements]
        if node.type == 'ObjectLiteral':
            obj = {}
            for k, v in node.pairs:
                obj[k] = self._materialize_literal(v) if hasattr(v, 'type') else v
            return obj
        return None


def compile_to_register_code(ast):
    c = RegisterCompiler()
    instrs, consts, names, reg_count = c.compile_program(ast)
    return instrs, consts, names, reg_count
