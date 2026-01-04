import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from runtime.compiler import compile_to_ast
from runtime.bytecode_compiler import compile_to_bytecode
from runtime.vm import VM

code = '''
function add(a, b):
    return a + b
end

result = add(2, 3)
'''
ast = compile_to_ast(code)
instrs, consts, names = compile_to_bytecode(ast)
vm = VM()
vm.run(instrs, consts=consts, names=names)
assert vm.globals.get('result') == 5
print('test_bytecode_function passed')
