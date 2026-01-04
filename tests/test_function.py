import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from runtime.compiler import compile_to_ast
from runtime.interpreter import Interpreter

code = '''
function add(a, b):
    return a + b
end

result = add(2, 3)
'''

ast = compile_to_ast(code)
interp = Interpreter()
interp.interpret(ast)

assert interp.variables.get('result') == 5
print('test_function passed')
