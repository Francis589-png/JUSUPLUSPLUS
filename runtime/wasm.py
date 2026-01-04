"""WASM runtime support (optional dependency on wasmtime)

- Provides a small wrapper around `wasmtime` when available.
- Functions:
  - available() -> bool
  - instantiate_wat(text) -> WasmInstance
  - instantiate_file(path) -> WasmInstance

WasmInstance exposes `call(export_name, *args)` to invoke exported functions.

If `wasmtime` is not installed, the module still imports but functions raise helpful errors.
"""
from __future__ import annotations

from typing import Any, Optional

try:
    from wasmtime import Engine, Store, Module, Instance
    HAS_WASMTIME = True
except Exception:
    Engine = Store = Module = Instance = None
    HAS_WASMTIME = False


class WasmError(RuntimeError):
    pass


def available() -> bool:
    return HAS_WASMTIME


class WasmInstance:
    def __init__(self, instance):
        self._inst = instance

    def call(self, name: str, *args):
        if not HAS_WASMTIME:
            raise WasmError('wasmtime not available; install wasmtime to use wasm features')
        fn = self._inst.exports.get(name)
        if fn is None:
            raise WasmError(f"Export '{name}' not found in wasm module")
        return fn(*args)


def instantiate_wat(wat_text: str) -> WasmInstance:
    """Instantiate a WAT (text) module and return a WasmInstance.
    Requires wasmtime; otherwise raises `WasmError`.
    """
    if not HAS_WASMTIME:
        raise WasmError('wasmtime not available; please `pip install wasmtime`')
    engine = Engine()
    module = Module(engine, wat_text)
    store = Store(engine)
    inst = Instance(store, module, [])
    return WasmInstance(inst)


def instantiate_file(path: str) -> WasmInstance:
    if not HAS_WASMTIME:
        raise WasmError('wasmtime not available; please `pip install wasmtime`')
    engine = Engine()
    module = Module.from_file(engine, path)
    store = Store(engine)
    inst = Instance(store, module, [])
    return WasmInstance(inst)
