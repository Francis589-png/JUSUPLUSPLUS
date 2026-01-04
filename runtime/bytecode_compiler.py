"""
Simple AST -> Bytecode compiler for a minimal subset of Jusu++
Produces (instructions, consts, names) for top-level programs and functions.

Supported AST nodes: NumberLiteral, StringLiteral, BooleanLiteral, Identifier,
Assignment, BinaryExpression (+ - * /), CallExpression, FunctionDeclaration, ReturnStatement,
SayStatement (ignored at bytecode compile; handled in top-level by storing prints),
ArrayLiteral and ObjectLiteral are compiled as constants.

This is intentionally small and conservative — target is to demonstrate VM performance.
"""

from compiler.parser import ASTNode

# Opcodes (match runtime/vm.py)
LOAD_CONST = 1
LOAD_NAME = 2
STORE_NAME = 3
BINARY_ADD = 4
BINARY_SUB = 5
BINARY_MUL = 6
BINARY_DIV = 7
RETURN_VALUE = 8
CALL_FUNCTION = 9
JUMP_IF_FALSE = 10
JUMP = 11
BINARY_LT = 12
BINARY_GT = 13
BINARY_LE = 14
BINARY_GE = 15
BINARY_EQ = 16
BINARY_NE = 17
BINARY_ADD_FAST = 18

class BytecodeCompiler:
    def __init__(self):
        self.consts = []
        self.names = []
        self.instructions = []

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

    def compile_program(self, ast):
        # compile a list of statements
        for stmt in ast:
            self.compile_stmt(stmt)
        # ensure top-level returns None
        self.instructions.append((RETURN_VALUE, None))
        return self.instructions, self.consts, self.names

    def compile_stmt(self, node):
        # Helper to append instruction
        def emit(op, arg=None):
            self.instructions.append((op, arg))

        if node.type == 'Assignment':
            self.compile_expr(node.value)
            name_idx = self._add_name(node.name)
            emit(STORE_NAME, name_idx)
        elif node.type == 'FunctionDeclaration':
            # compile function body into a code object
            compiler = BytecodeCompiler()
            # parameters are names local to function
            for p in node.params:
                compiler._add_name(p)
            for s in node.body:
                compiler.compile_stmt(s)
            compiler.instructions.append((RETURN_VALUE, None))
            code_obj = ('code', compiler.instructions, compiler.consts, compiler.names, node.params)
            const_idx = self._add_const(code_obj)
            name_idx = self._add_name(node.name)
            emit(LOAD_CONST, const_idx)
            emit(STORE_NAME, name_idx)
        elif node.type == 'ReturnStatement':
            if node.value is not None:
                self.compile_expr(node.value)
            else:
                emit(LOAD_CONST, self._add_const(None))
            emit(RETURN_VALUE, None)
        elif node.type == 'ExpressionStatement':
            self.compile_expr(node.expression)
            # drop result (not implemented: POP_TOP), so just ignore
        elif node.type == 'SayStatement':
            # compile say X -> load built-in print and call
            self.compile_expr(node.expression)
            # load print
            nm = self._add_name('print')
            emit(LOAD_NAME, nm)
            emit(CALL_FUNCTION, 1)
        elif node.type == 'IfStatement':
            # compile condition
            self.compile_expr(node.condition)
            # placeholder for jump-if-false
            jif_pos = len(self.instructions)
            emit(JUMP_IF_FALSE, None)
            # then branch
            for s in node.then_branch:
                self.compile_stmt(s)
            if node.else_branch:
                # jump over else
                jmp_pos = len(self.instructions)
                emit(JUMP, None)
                # patch JUMP_IF_FALSE to point to start of else
                self.instructions[jif_pos] = (JUMP_IF_FALSE, len(self.instructions))
                for s in node.else_branch:
                    self.compile_stmt(s)
                # patch JUMP to after else
                self.instructions[jmp_pos] = (JUMP, len(self.instructions))
            else:
                # patch JUMP_IF_FALSE to after then-branch
                self.instructions[jif_pos] = (JUMP_IF_FALSE, len(self.instructions))
        else:
            raise NotImplementedError(f"Statement compile not implemented: {node.type}")

    def compile_expr(self, node):
        t = node.type
        if t == 'NumberLiteral' or t == 'StringLiteral' or t == 'BooleanLiteral' or t == 'ObjectLiteral' or t == 'ArrayLiteral':
            idx = self._add_const(self._materialize_literal(node))
            self.instructions.append((LOAD_CONST, idx))
        elif t == 'Identifier':
            name_idx = self._add_name(node.name)
            self.instructions.append((LOAD_NAME, name_idx))
        elif t == 'BinaryExpression':
            # Constant-fold numeric binary expressions
            if node.left.type == 'NumberLiteral' and node.right.type == 'NumberLiteral':
                left_val = node.left.value
                right_val = node.right.value
                op = node.operator
                if op == '+':
                    val = left_val + right_val
                elif op == '-':
                    val = left_val - right_val
                elif op == '*':
                    val = left_val * right_val
                elif op == '/':
                    val = left_val / right_val
                else:
                    raise NotImplementedError(f"Binary op {op} not supported in constant folding")
                idx = self._add_const(val)
                self.instructions.append((LOAD_CONST, idx))
                return

            self.compile_expr(node.left)
            self.compile_expr(node.right)
            op = node.operator
            if op == '+':
                # emit a fast numeric add opcode that optimizes the common numeric case
                self.instructions.append((BINARY_ADD_FAST, None))
            elif op == '-':
                self.instructions.append((BINARY_SUB, None))
            elif op == '*':
                self.instructions.append((BINARY_MUL, None))
            elif op == '/':
                self.instructions.append((BINARY_DIV, None))
            elif op == '<':
                self.instructions.append((BINARY_LT, None))
            elif op == '>':
                self.instructions.append((BINARY_GT, None))
            elif op == '<=':
                self.instructions.append((BINARY_LE, None))
            elif op == '>=':
                self.instructions.append((BINARY_GE, None))
            elif op == '==':
                self.instructions.append((BINARY_EQ, None))
            elif op == '!=':
                self.instructions.append((BINARY_NE, None))
            else:
                raise NotImplementedError(f"Binary op {op} not supported in bytecode")
        elif t == 'CallExpression':
            # compile callee (could be dotted name compiled as Identifier with name 'a.b')
            # for simplicity we resolve callee at runtime via name lookup
            # push args first then load callee
            for arg in node.arguments:
                self.compile_expr(arg)
            # callee
            # If callee looks like dotted name, we still make it a LOAD_NAME of the dotted string
            name_idx = self._add_name(node.callee)
            self.instructions.append((LOAD_NAME, name_idx))
            self.instructions.append((CALL_FUNCTION, len(node.arguments)))
        else:
            raise NotImplementedError(f"Expr compile not implemented: {t}")

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

# convenience function

def compile_to_bytecode(ast):
    c = BytecodeCompiler()
    instrs, consts, names = c.compile_program(ast)
    return instrs, consts, names
