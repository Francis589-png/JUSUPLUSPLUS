import os
import sys
import platform
# Ensure project root on sys.path when running test as script
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from runtime.ffi import load, FFIError


def test_load_lib_and_call_simple_function():
    # Load libc or msvcrt depending on platform and call a simple function
    if platform.system() == 'Windows':
        libname = 'msvcrt'
        # msvcrt has _atoi64 or atoi
        funcname = 'atoi'
        argtypes = ['cstr']
        restype = 'i64'
    else:
        libname = 'c'
        funcname = 'atoi'
        argtypes = ['cstr']
        restype = 'i64'

    lib = load(libname)
    fn = lib.func(funcname, restype=restype, argtypes=argtypes)
    assert fn(b'123') == 123 or fn('123') == 123


def test_missing_symbol_raises():
    import platform
    libname = 'msvcrt' if platform.system() == 'Windows' else 'c'
    lib = load(libname)
    try:
        lib.func('this_symbol_does_not_exist')
        assert False, 'Expected FFIError'
    except FFIError:
        pass
