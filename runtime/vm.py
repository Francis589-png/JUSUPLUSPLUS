"""
Simple VM skeleton for Jusu++ (proof of concept)
"""

# Define opcodes (match runtime/bytecode_compiler.py)
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

class VM:
    def __init__(self):
        self.consts = []
        self.names = []
        self.stack = []
        self.pc = 0
        self.instructions = []
        self.globals = {}
        # Inline caches for fast name/attribute lookup: maps name -> value
        # On STORE_NAME we update the cache for the affected name; on LOAD_NAME
        # we check the cache first. This is a simple form of inline caching.
        self.name_cache = {}
        # Call frame stack to avoid creating new VM instances on each call
        # Each frame is a dict with keys: instructions, consts, names, pc, locals
        self.call_stack = []
        self.locals = None

    def run(self, instructions, consts=None, names=None):
        self.instructions = instructions
        self.consts = consts or []
        self.names = names or []
        self.pc = 0
        self.stack = []

        while self.pc < len(self.instructions):
            op, arg = self.instructions[self.pc]
            self.pc += 1
            if op == LOAD_CONST:
                self.stack.append(self.consts[arg])
            elif op == LOAD_NAME:
                name = self.names[arg]
                # Check locals first (function params/local variables)
                if self.locals is not None and name in self.locals:
                    self.stack.append(self.locals.get(name))
                    continue
                # Check inline cache for globals
                if name in self.name_cache:
                    self.stack.append(self.name_cache[name])
                    continue

                # Resolve dotted names (e.g., 'math.sqrt') by traversing
                if '.' in name:
                    parts = name.split('.')
                    obj = self.globals.get(parts[0])
                    for p in parts[1:]:
                        try:
                            if hasattr(obj, p):
                                obj = getattr(obj, p)
                            else:
                                obj = obj[p]
                        except Exception:
                            obj = None
                            break
                    value = obj
                else:
                    value = self.globals.get(name)

                # Cache the resolved global value for subsequent fast lookup
                self.name_cache[name] = value
                self.stack.append(value)
            elif op == STORE_NAME:
                name = self.names[arg]
                val = self.stack.pop()
                self.globals[name] = val
                # Update the inline cache so future loads are fast
                self.name_cache[name] = val
            elif op == BINARY_ADD:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a + b)
            elif op == BINARY_ADD_FAST:
                b = self.stack.pop()
                a = self.stack.pop()
                # Fast-path for numeric types
                if (isinstance(a, (int, float)) and isinstance(b, (int, float))):
                    self.stack.append(a + b)
                else:
                    # fallback to python addition
                    self.stack.append(a + b)
            elif op == BINARY_SUB:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a - b)
            elif op == BINARY_MUL:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a * b)
            elif op == BINARY_DIV:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a / b)
            elif op == BINARY_LT:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a < b)
            elif op == BINARY_GT:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a > b)
            elif op == BINARY_LE:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a <= b)
            elif op == BINARY_GE:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a >= b)
            elif op == BINARY_EQ:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a == b)
            elif op == BINARY_NE:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a != b)
            elif op == BINARY_ADD_FAST:
                b = self.stack.pop()
                a = self.stack.pop()
                # Fast-path for numeric types
                if (isinstance(a, (int, float)) and isinstance(b, (int, float))):
                    self.stack.append(a + b)
                else:
                    # fallback to python addition
                    self.stack.append(a + b)
            elif op == CALL_FUNCTION:
                argc = arg
                # Pop callee then args
                fn = self.stack.pop()
                args = [self.stack.pop() for _ in range(argc)][::-1]
                # If fn is a compiled code object: ('code', instrs, consts, names, params)
                if isinstance(fn, tuple) and len(fn) >= 5 and fn[0] == 'code':
                    _, instrs, consts, names, params = fn
                    # Push current frame
                    frame = {
                        'instructions': self.instructions,
                        'consts': self.consts,
                        'names': self.names,
                        'pc': self.pc,
                        'locals': self.locals,
                    }
                    self.call_stack.append(frame)
                    # Set up new frame for function
                    self.instructions = instrs
                    self.consts = consts
                    self.names = names
                    self.locals = {}
                    for p, a in zip(params, args):
                        self.locals[p] = a
                    self.pc = 0
                elif callable(fn):
                    self.stack.append(fn(*args))
                else:
                    raise TypeError(f"Object of type {type(fn).__name__} is not callable")
            elif op == JUMP_IF_FALSE:
                target = arg
                cond = self.stack.pop()
                if not cond:
                    self.pc = target
            elif op == JUMP:
                self.pc = arg
            elif op == RETURN_VALUE:
                ret = self.stack.pop() if self.stack else None
                # If we're in a function call (call_stack not empty), pop frame and restore
                if self.call_stack:
                    frame = self.call_stack.pop()
                    # restore caller state
                    self.instructions = frame['instructions']
                    self.consts = frame['consts']
                    self.names = frame['names']
                    self.locals = frame['locals']
                    self.pc = frame['pc']
                    # push return value for caller
                    self.stack.append(ret)
                    continue
                return ret
            else:
                raise NotImplementedError(f"Opcode {op} not implemented")
        return None
