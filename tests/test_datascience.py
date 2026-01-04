import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from runtime.compiler import compile_to_ast
from runtime.interpreter import Interpreter

code = '''
arr = np.array([1,2,3])
s = np.sum(arr)
m = np.mean(arr)
'''

ast = compile_to_ast(code)
interp = Interpreter()
interp.interpret(ast)

# sum and mean should be available whether numpy is installed or not
assert interp.variables['s'] == 6
assert abs(interp.variables['m'] - 2.0) < 1e-9
print('test_datascience passed')
