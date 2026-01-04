import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from runtime.compiler import compile_to_ast
from runtime.interpreter import Interpreter

code = '''
x = 10
if x > 5:
    y is 1
end
if x < 5:
    y is 2
else:
    y is 3
end
'''

ast = compile_to_ast(code)
interp = Interpreter()
interp.interpret(ast)

assert interp.variables.get('y') == 3
print('test_if passed')
