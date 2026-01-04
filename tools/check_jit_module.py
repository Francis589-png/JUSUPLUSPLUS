import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import runtime.jit as jit
print('jit module file:', getattr(jit, '__file__', 'no file'))
print('has compile_simple_function:', hasattr(jit, 'compile_simple_function'))
import inspect
print('source snippet:')
print('\n'.join(inspect.getsource(jit.compile_simple_function).splitlines()[:40]))
