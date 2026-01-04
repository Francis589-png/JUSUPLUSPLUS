import os
import sys
import time

# Ensure project root is on sys.path so imports work when run as a script
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from runtime.compiler import compile_and_run

# Create a small program that defines a multi-arg numeric function and calls it many times
N = 20000
lines = []
lines.append('function hot(a, b, c):')
lines.append('    return (a * b) + (b * c) - (c - a)')
lines.append('end')
lines.append('s = 0')
for i in range(N):
    a = i - (i // 10) * 10
    b = (i + 3) - ((i + 3) // 7) * 7
    c = (i + 5) - ((i + 5) // 13) * 13
    lines.append(f's = s + hot({a}, {b}, {c})')
lines.append('say s')

src = '\n'.join(lines) + '\n'

p = 'tmp_jit_bench.jusu'
open(p, 'w').write(src)

backends = ['interp', 'vm', 'regvm']

for b in backends:
    t0 = time.time()
    compile_and_run(p, backend=b)
    dt = time.time() - t0
    print(f"backend={b} time={dt:.4f}s")
