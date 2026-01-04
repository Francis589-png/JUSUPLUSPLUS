import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from runtime.compiler import compile_to_ast

# Syntax error should include line number
try:
    compile_to_ast('name is "Alice"\n} unexpected')
    raise SystemExit('Expected SyntaxError')
except SyntaxError as e:
    assert '[Line' in str(e)

# AST nodes should have line and column metadata
ast = compile_to_ast('say "Hi"\n')
first = ast[0]
assert getattr(first, 'line', None) is not None
assert getattr(first, 'column', None) is not None
print('test_errors_and_locations passed')
