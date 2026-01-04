import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.benchmarks import SAMPLES
from runtime.compiler import compile_to_ast
from runtime.register_compiler import compile_to_register_code

src = SAMPLES['fib_recursive']
print('len src lines', len(src.splitlines()))
ast = compile_to_ast(src)
print('AST len', len(ast))
instrs, consts, names, reg_count = compile_to_register_code(ast)
print('instrs len', len(instrs), 'consts len', len(consts), 'names len', len(names), 'reg_count', reg_count)
for i, ins in enumerate(instrs[:400]):
    print(i, ins)

print('\nconsts:')
for i, c in enumerate(consts):
    if isinstance(c, tuple) and c and c[0] == 'regcode':
        print(i, 'regcode with', len(c[1]), 'instrs, consts', len(c[2]), 'names', len(c[3]), 'params', c[4], 'regs', c[5])
        for j, ins in enumerate(c[1]):
            print('   ', j, ins)
    else:
        print(i, c)

print('\nnames:')
for i, n in enumerate(names):
    print(i, n)

