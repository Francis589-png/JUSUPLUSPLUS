import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from runtime.compiler import compile_to_ast
from runtime.interpreter import Interpreter

code = '''
val = math.sqrt(16)
js = json.dumps({'a':1})
'''
ast = compile_to_ast(code)
interp = Interpreter()
interp.interpret(ast)

assert abs(interp.variables['val'] - 4.0) < 1e-6
assert interp.variables['js'].startswith('{')
print('test_stdlib passed')
