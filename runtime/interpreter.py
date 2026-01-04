"""
Jusu++ Interpreter - Executes the AST
"""

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class Interpreter:
    """Executes Jusu++ AST"""

    def __init__(self):
        self.variables = {}  # Store variable values
        # Builtin functions
        self.builtins = {
            'str': lambda x: str(x),
            'int': lambda x: int(x),
            'float': lambda x: float(x),
            'len': lambda x: len(x),
            'print': lambda *args: print(*args),
            'range': lambda *args: list(range(*map(int, args))),
            'sum': lambda seq: sum(seq),
            'max': lambda seq: max(seq),
            'min': lambda seq: min(seq),
            'list': lambda *args: list(args),
            'dict': lambda **kwargs: dict(**kwargs),
            'append': lambda seq, v: (seq.append(v), seq)[1],
        }

        # Load stdlib if available (adds modules like math, json)
        try:
            from runtime import stdlib as _stdlib
            for name, val in _stdlib.get_builtins().items():
                # Prefer existing builtins but expose stdlib modules in variables
                self.variables[name] = val
        except Exception:
            # If stdlib import fails, continue without it
            pass

    def _node_loc(self, node):
        if not node:
            return ''
        line = getattr(node, 'line', None)
        col = getattr(node, 'column', None)
        if line is None:
            return ''
        if col is None:
            return f" (at line {line})"
        return f" (at line {line}, col {col})"

    def _resolve_callable(self, callee):
        """Resolve callee which may be a name or a callable."""
        if callable(callee):
            return callee
        if isinstance(callee, str):
            # First check builtins
            if callee in self.builtins:
                return self.builtins[callee]
            if callee in self.variables and callable(self.variables[callee]):
                return self.variables[callee]
        raise NameError(f"Function '{callee}' is not defined or not callable")
    def interpret(self, ast):
        """Execute a list of AST nodes"""
        for node in ast:
            self.execute(node)

    def execute(self, node):
        """Execute a single AST node"""
        node_type = node.type

        if node_type == 'SayStatement':
            value = self.evaluate(node.expression)
            print(value)

        elif node_type == 'Assignment':
            value = self.evaluate(node.value)
            self.variables[node.name] = value

        elif node_type == 'ExpressionStatement':
            self.evaluate(node.expression)

        elif node_type == 'FunctionDeclaration':
            name = node.name
            params = node.params
            body = node.body
            # Store a callable wrapper that tracks hotness and may be JIT-compiled
            class JITFunction:
                def __init__(self, outer, node):
                    self.outer = outer
                    self.node = node
                    self.call_count = 0
                    self.jit_wrapper = None

                def __call__(self, *args):
                    # If JIT compiled, call native impl
                    if self.jit_wrapper is not None:
                        return self.jit_wrapper(*args)

                    # Otherwise call interpreter-based function
                    self.call_count += 1
                    # Attempt to JIT after threshold
                    THRESHOLD = 8
                    if self.call_count >= THRESHOLD and self.jit_wrapper is None:
                        try:
                            print(f"[JIT] Attempting to compile '{self.node.name}' (calls={self.call_count})")
                            from runtime import jit
                            compiled = jit.compile_simple_function(self.node)
                            if compiled is not None:
                                print(f"[JIT] '{self.node.name}' compiled successfully")
                                self.jit_wrapper = compiled
                            else:
                                print(f"[JIT] '{self.node.name}' not eligible for JIT compilation")
                        except Exception as e:
                            # ignore JIT failures and continue
                            print(f"[JIT] compilation raised: {e}")
                            pass

                    child = Interpreter()
                    child.variables = self.outer.variables.copy()
                    child.builtins = self.outer.builtins
                    for p, a in zip(self.node.params, args):
                        child.variables[p] = a
                    try:
                        for stmt in self.node.body:
                            child.execute(stmt)
                    except ReturnException as re:
                        return re.value
                    return None

            self.variables[name] = JITFunction(self, node)

        elif node_type == 'IfStatement':
            cond = self.evaluate(node.condition)
            if cond:
                for stmt in node.then_branch:
                    self.execute(stmt)
            elif node.else_branch:
                for stmt in node.else_branch:
                    self.execute(stmt)

        elif node_type == 'ReturnStatement':
            value = self.evaluate(node.value) if getattr(node, 'value', None) is not None else None
            raise ReturnException(value)

        else:
            raise RuntimeError(f"Unknown node type: {node_type}")
    
    def evaluate(self, node):
        """Evaluate an expression node to a value"""
        node_type = node.type
        
        if node_type == 'NumberLiteral':
            return node.value
        
        elif node_type == 'StringLiteral':
            return node.value
        
        elif node_type == 'BooleanLiteral':
            return node.value

        elif node_type == 'ObjectLiteral':
            obj = {}
            for k, v in node.pairs:
                obj[k] = self.evaluate(v)
            return obj

        elif node_type == 'ArrayLiteral':
            return [self.evaluate(e) for e in node.elements]
        
        elif node_type == 'Identifier':
            name = node.name
            # Support dotted identifiers like 'math.pi'
            if '.' in name:
                parts = name.split('.')
                base = parts[0]
                if base in self.variables:
                    obj = self.variables[base]
                    for attr in parts[1:]:
                        try:
                            if hasattr(obj, attr):
                                obj = getattr(obj, attr)
                            elif isinstance(obj, dict) and attr in obj:
                                obj = obj[attr]
                            else:
                                raise NameError(f"Attribute '{attr}' not found on '{base}'" + self._node_loc(node))
                        except Exception:
                            raise NameError(f"Attribute '{attr}' not found on '{base}'" + self._node_loc(node))
                    return obj
                else:
                    raise NameError(f"Name '{base}' is not defined" + self._node_loc(node))
            if name in self.variables:
                return self.variables[name]
            else:
                raise NameError(f"Variable '{name}' is not defined" + self._node_loc(node))

        elif node_type == 'BinaryExpression':
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            operator = node.operator

            # Handle arithmetic operations with type checks
            if operator == '+':
                # Strict rules: strings must be concatenated only when both operands are strings
                if isinstance(left, str) and isinstance(right, str):
                    return left + right
                # Numeric addition
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    return left + right
                raise TypeError(f"Cannot apply '+' to types {type(left).__name__} and {type(right).__name__}" + self._node_loc(node))
            elif operator == '-':
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    return left - right
                raise TypeError(f"Cannot apply '-' to types {type(left).__name__} and {type(right).__name__}")
            elif operator == '*':
                # Allow string * int repetition
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    return left * right
                if isinstance(left, str) and isinstance(right, int):
                    return left * right
                if isinstance(right, str) and isinstance(left, int):
                    return right * left
                raise TypeError(f"Cannot apply '*' to types {type(left).__name__} and {type(right).__name__}")
            elif operator == '/':
                if not (isinstance(left, (int, float)) and isinstance(right, (int, float))):
                    raise TypeError(f"Cannot apply '/' to types {type(left).__name__} and {type(right).__name__}")
                if right == 0:
                    raise ZeroDivisionError("Division by zero")
                return left / right
            elif operator in ('==','!=','<','>','<=','>='):
                # Python's native comparisons are fine; provide clearer error if incomparable
                try:
                    if operator == '==':
                        return left == right
                    elif operator == '!=':
                        return left != right
                    elif operator == '<':
                        return left < right
                    elif operator == '>':
                        return left > right
                    elif operator == '<=':
                        return left <= right
                    elif operator == '>=':
                        return left >= right
                except TypeError:
                    raise TypeError(f"Cannot compare types {type(left).__name__} and {type(right).__name__}")
            else:
                raise RuntimeError(f"Unknown operator: {operator}")
        
        elif node_type == 'CallExpression':
            callee = node.callee
            args = [self.evaluate(arg) for arg in node.arguments]
            # Handle dotted names like 'math.sqrt'
            if isinstance(callee, str) and '.' in callee:
                parts = callee.split('.')
                base = parts[0]
                if base in self.variables:
                    obj = self.variables[base]
                    for attr in parts[1:]:
                        # Prefer attribute access, fallback to dict-like
                        if hasattr(obj, attr):
                            obj = getattr(obj, attr)
                        elif isinstance(obj, dict) and attr in obj:
                            obj = obj[attr]
                        else:
                            raise NameError(f"Attribute '{attr}' not found on '{base}'" + self._node_loc(node))
                    if callable(obj):
                        try:
                            return obj(*args)
                        except Exception as e:
                            raise RuntimeError(str(e) + self._node_loc(node))
                    raise NameError(f"Attribute '{parts[-1]}' is not callable" + self._node_loc(node))
                else:
                    raise NameError(f"Name '{base}' is not defined" + self._node_loc(node))

            # Check built-ins first
            if callee in self.builtins:
                return self.builtins[callee](*args)
            # Check for user-defined callables (stored in variables)
            if callee in self.variables and callable(self.variables[callee]):
                return self.variables[callee](*args)
            raise NameError(f"Function '{callee}' is not defined" + self._node_loc(node))
        
        else:
            raise RuntimeError(f"Cannot evaluate node type: {node_type}")

# Test function
def test_interpreter():
    """Test the interpreter"""
    from compiler.lexer import Lexer
    from compiler.parser import Parser
    
    code = '''
    name is "Alice"
    age = 20 + 5
    say "Hello " + name
    say "Age: " + str(age)
    '''
    
    # Lexical analysis
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    
    # Parsing
    parser = Parser(tokens)
    ast = parser.parse()
    
    # Interpretation
    interpreter = Interpreter()
    interpreter.interpret(ast)

if __name__ == "__main__":
    test_interpreter()