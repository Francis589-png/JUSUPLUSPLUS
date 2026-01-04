import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from runtime.compiler import compile_to_ast
from runtime.interpreter import Interpreter

code = '''
nums = list(1, 2, 3, 4)
s = sum(nums)
mx = max(nums)
mn = min(nums)
seq = list('a','b')
append(seq, 'c')
'''
ast = compile_to_ast(code)
interp = Interpreter()
interp.interpret(ast)

assert interp.variables['s'] == 10
assert interp.variables['mx'] == 4
assert interp.variables['mn'] == 1
assert interp.variables['seq'] == ['a','b','c']
print('test_builtins passed')
