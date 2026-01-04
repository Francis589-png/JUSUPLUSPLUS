"""
A minimal register-based VM for the subset compiled by `register_compiler`.
This is an experimental prototype to measure performance for arithmetic and name lookups.
"""

class RegisterVM:
    def __init__(self):
        self.consts = []
        self.names = []
        self.instructions = []
        self.regs = []
        self.pc = 0
        self.globals = {}
        # reuse frames to avoid allocations
        self.call_stack = []

    def run(self, instructions, consts=None, names=None, reg_count=32):
        self.instructions = instructions
        self.consts = consts or []
        self.names = names or []
        self.pc = 0
        # allocate register file
        self.regs = [None] * max(reg_count, 32)

        while self.pc < len(self.instructions):
            ins = self.instructions[self.pc]
            self.pc += 1
            op = ins[0]
            if op == 'LOADC':
                _, dst, cidx = ins
                self.regs[dst] = self.consts[cidx]
            elif op == 'LOAD_NAME':
                _, dst, nidx = ins
                name = self.names[nidx]
                # simple dotted resolution
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
                    self.regs[dst] = obj
                else:
                    self.regs[dst] = self.globals.get(name)
            elif op == 'STORE_NAME':
                _, nidx, src = ins
                name = self.names[nidx]
                self.globals[name] = self.regs[src]
            elif op == 'ADD':
                _, dst, r1, r2 = ins
                self.regs[dst] = self.regs[r1] + self.regs[r2]
            elif op == 'SUB':
                _, dst, r1, r2 = ins
                self.regs[dst] = self.regs[r1] - self.regs[r2]
            elif op == 'MUL':
                _, dst, r1, r2 = ins
                self.regs[dst] = self.regs[r1] * self.regs[r2]
            elif op == 'DIV':
                _, dst, r1, r2 = ins
                self.regs[dst] = self.regs[r1] / self.regs[r2]
            elif op == 'LT':
                _, dst, r1, r2 = ins
                self.regs[dst] = self.regs[r1] < self.regs[r2]
            elif op == 'GT':
                _, dst, r1, r2 = ins
                self.regs[dst] = self.regs[r1] > self.regs[r2]
            elif op == 'LE':
                _, dst, r1, r2 = ins
                self.regs[dst] = self.regs[r1] <= self.regs[r2]
            elif op == 'GE':
                _, dst, r1, r2 = ins
                self.regs[dst] = self.regs[r1] >= self.regs[r2]
            elif op == 'EQ':
                _, dst, r1, r2 = ins
                self.regs[dst] = self.regs[r1] == self.regs[r2]
            elif op == 'NE':
                _, dst, r1, r2 = ins
                self.regs[dst] = self.regs[r1] != self.regs[r2]
            elif op == 'CALL':
                _, dst, fn_reg, arg_regs = ins
                fn = self.regs[fn_reg]
                args = [self.regs[r] for r in arg_regs]
                if isinstance(fn, tuple) and fn and fn[0] == 'regcode':
                    # push current frame
                    # push current frame including where the caller expects the return value (dst)
                    frame = {
                        'instructions': self.instructions,
                        'consts': self.consts,
                        'names': self.names,
                        'pc': self.pc,
                        'regs': self.regs,
                        'return_reg': dst,
                    }
                    self.call_stack.append(frame)
                    _, fn_instrs, fn_consts, fn_names, param_count, fn_reg_count = fn
                    self.instructions = fn_instrs
                    self.consts = fn_consts
                    self.names = fn_names
                    self.pc = 0
                    # create new regs sized to fn_reg_count
                    self.regs = [None] * fn_reg_count
                    # copy args into first N registers
                    for i, a in enumerate(args[:param_count]):
                        self.regs[i] = a
                elif callable(fn):
                    res = fn(*args)
                    if dst is not None:
                        self.regs[dst] = res
                    # if dst is None, discard result (e.g., print)
                else:
                    raise TypeError(f"Object of type {type(fn).__name__} is not callable")
            elif op == 'RETURN':
                _, src = ins
                ret = self.regs[src] if src is not None else None
                if self.call_stack:
                    frame = self.call_stack.pop()
                    instructions = frame['instructions']
                    consts = frame['consts']
                    names = frame['names']
                    pc = frame['pc']
                    regs = frame['regs']
                    return_reg = frame.get('return_reg')
                    self.instructions = instructions
                    self.consts = consts
                    self.names = names
                    self.pc = pc
                    self.regs = regs
                    # store return value into the caller's expected register (if provided)
                    if return_reg is not None:
                        self.regs[return_reg] = ret
                    else:
                        # fallback to r0
                        self.regs[0] = ret
                    continue
                return ret
            else:
                raise NotImplementedError(f"RegVM: opcode {op} not implemented")
        return None
