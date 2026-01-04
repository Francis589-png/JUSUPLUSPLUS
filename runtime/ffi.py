"""Simple ctypes-based FFI helper for Jusu++

Provides a tiny convenience for loading shared libraries and invoking exported
functions with simple type annotations. This is intentionally small: for full
features, users should write a Python extension or use `pybind11` / `cffi`.

API:
- load(path) -> Lib object
  - lib.get(name, restype='i64'|'f64'|'cstr', argtypes=[...]) -> callable
  - lib.func(name, restype='i64'|'f64'|'cstr', argtypes=[...]) -> callable

Type tags: 'i64' -> 64-bit signed integer, 'f64' -> double, 'cstr' -> C string

Example (Jusu usage):
  lib = ffi.load('/usr/lib/libm.so')
  sin = lib.func('sin', restype='f64', argtypes=['f64'])
  print(sin(0.0))
"""
from __future__ import annotations

import ctypes
import sys
import os
from typing import Any, List


_type_map = {
    'i64': ctypes.c_longlong,
    'f64': ctypes.c_double,
    'cstr': ctypes.c_char_p,
}


class FFIError(RuntimeError):
    pass


class Lib:
    def __init__(self, path: str):
        if not os.path.exists(path) and not os.path.isabs(path):
            # allow resolving by name (e.g. 'c' -> libc)
            pass
        try:
            self._lib = ctypes.CDLL(path)
        except Exception as e:
            raise FFIError(f"Failed to load library {path}: {e}")
        self.path = path

    def func(self, name: str, restype: str = 'i64', argtypes: List[str] = None):
        """Return a callable wrapper around the named symbol."""
        if argtypes is None:
            argtypes = []
        c_rest = _type_map.get(restype)
        if c_rest is None:
            raise FFIError(f"Unknown restype: {restype}")
        try:
            f = getattr(self._lib, name)
        except AttributeError:
            raise FFIError(f"Symbol '{name}' not found in {self.path}")
        f.restype = c_rest
        f.argtypes = [(_type_map.get(t) or ctypes.c_void_p) for t in argtypes]

        def call(*args):
            # encode strings if cstr
            cargs = []
            for t, a in zip(argtypes, args):
                if t == 'cstr' and isinstance(a, str):
                    cargs.append(a.encode('utf-8'))
                else:
                    cargs.append(a)
            return f(*cargs)

        return call

    # convenience alias
    get = func


def load(path: str) -> Lib:
    """Load a shared library by path or conventional name.

    On Unix, common names like 'c' or 'm' can be used (ctypes resolves via ld).
    On Windows, use 'msvcrt' or full DLL path.
    """
    # Let ctypes handle name resolution; just forward to Lib
    return Lib(path)
