import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.benchmarks import build_name_lookup_program
from runtime.compiler import compile_to_ast

src = build_name_lookup_program(repeats=1500)
lines = src.splitlines()
print('LEN', len(lines))
print('\n-- tail lines --')
for i, line in enumerate(lines[-40:], start=len(lines)-39):
    print(f"{i}: {line!r}")

try:
    compile_to_ast(src)
    print('\nParse OK')
except Exception as e:
    import traceback
    print('\nParse FAILED')
    traceback.print_exc()
