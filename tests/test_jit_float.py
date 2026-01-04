import pytest

try:
    from runtime import jit
    HAS_LLVM = getattr(jit, '_HAS_LLVM', False)
except Exception:
    HAS_LLVM = False


@pytest.mark.skipif(not HAS_LLVM, reason="llvmlite not available")
def test_jit_compiles_float_function():
    from compiler.lexer import Lexer
    from compiler.parser import Parser

    src = '''
function f(a, b):
    return a / b + 1.5
end
'''
    lexer = Lexer(src)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    fn = None
    for node in ast:
        if node.type == 'FunctionDeclaration' and node.name == 'f':
            fn = node
            break
    assert fn is not None

    compiled = jit.compile_simple_function(fn)
    assert compiled is not None

    # Call compiled function
    res = compiled(6, 4)
    assert abs(res - (6 / 4 + 1.5)) < 1e-9
