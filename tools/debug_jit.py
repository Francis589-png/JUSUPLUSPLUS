import os
import sys
# ensure repo root
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from compiler.lexer import Lexer
from compiler.parser import Parser

p = 'tmp_jit_bench.jusu'
code = open(p).read()
lexer = Lexer(code)
tokens = lexer.tokenize()
parser = Parser(tokens)
ast = parser.parse()

# find function 'hot'
fn = None
for node in ast:
    if node.type == 'FunctionDeclaration' and node.name == 'hot':
        fn = node
        break

print('Found function hot:', bool(fn))
if fn:
    print('params=', fn.params)
    print('body_len=', len(fn.body))
    for s in fn.body:
        print('stmt type=', s.type)

try:
    from runtime import jit
    print('HAS_LLVM in jit module:', getattr(jit, '_HAS_LLVM', False))
    print('Trying to compile...')
    compiled = jit.compile_simple_function(fn)
    print('compile result:', compiled)
except Exception as e:
    import traceback
    print('Exception during JIT debug:')
    traceback.print_exc()
