import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from runtime.compiler import compile_to_ast
from runtime.interpreter import Interpreter

code = """
a is 'Hello\nWorld'
b = "Hi"
"""

ast = compile_to_ast(code)
interp = Interpreter()
interp.interpret(ast)

assert interp.variables['a'] == "Hello\nWorld"
assert interp.variables['b'] == "Hi"
print('test_strings passed')
