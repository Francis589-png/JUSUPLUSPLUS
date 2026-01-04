# Ensure project root is on sys.path when running tests
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from runtime.vm import VM, LOAD_CONST, LOAD_NAME, STORE_NAME, BINARY_ADD, RETURN_VALUE

# Build a program: a = 1; b = 2; c = a + b; return c
consts = [1,2]
names = ['a','b','c']
# instructions: LOAD_CONST 0 -> STORE_NAME 0; LOAD_CONST 1 -> STORE_NAME 1; LOAD_NAME 0; LOAD_NAME 1; BINARY_ADD; STORE_NAME 2; LOAD_NAME 2; RETURN_VALUE
instr = [
    (LOAD_CONST, 0),(STORE_NAME,0),
    (LOAD_CONST, 1),(STORE_NAME,1),
    (LOAD_NAME,0),(LOAD_NAME,1),(BINARY_ADD, None),(STORE_NAME,2),
    (LOAD_NAME,2),(RETURN_VALUE, None)
]
vm = VM()
res = vm.run(instr, consts=consts, names=names)
assert res == 3
print('test_vm_skeleton passed')
