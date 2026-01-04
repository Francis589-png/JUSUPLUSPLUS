import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from runtime.compiler import compile_to_ast
from runtime.interpreter import Interpreter

# Expect TypeError for numeric ops with strings
code = '''
a = 1 + 'x'
'''

ast = compile_to_ast(code)
interp = Interpreter()
try:
    interp.interpret(ast)
    raise SystemExit('Expected TypeError but none raised')
except TypeError as e:
    print('test_type_errors passed')
