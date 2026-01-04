# Interop Tutorial — FFI, WASM, JS, and Plugins

This short tutorial shows how to call native libraries, WebAssembly modules,
Node.js modules, and how to register/use third-party plugins with `arpah`.

## 1) FFI (ctypes) — quick example: atoi

```python
from runtime.ffi import load
# Load libc (platform-specific name)
lib = load('c' if os.name != 'nt' else 'msvcrt')
atoi = lib.func('atoi', restype='i64', argtypes=['cstr'])
print(atoi('123'))  # -> 123
```

Notes: `runtime.ffi` is a thin convenience around `ctypes`. For production
plugins consider writing proper C extensions (pybind11/cffi) or using WASM.

## 2) WASM — instantiate a WAT module and call an exported function

```python
from runtime import wasm
if not wasm.available():
    print('wasmtime not installed; install wasmtime to run wasm examples')
else:
    wat = '''
    (module
      (func $add (param $a i32) (param $b i32) (result i32)
        local.get $a
        local.get $b
        i32.add)
      (export "add" (func $add)))
    '''
    inst = wasm.instantiate_wat(wat)
    print(inst.call('add', 2, 3))  # -> 5
```

Note: WASM modules are portable and safer for running third-party native code.

## 3) JavaScript bridge (Node)

```python
from runtime import js
if not js.AVAILABLE:
    print('node not available; skip JS example')
else:
    # Create a local JS module example.js with `module.exports = { add: (a,b)=>a+b }`
    res = js.call('example.js', 'add', [2,3])
    print(res)
```

Use `runtime.sandbox.run_file` to execute untrusted JS in a subprocess with
timeouts and memory limits.

## 4) Plugins (Arpah)

- Package your plugin as a Python package that exposes an entry point in the
  `jusu.plugins` table (see `examples/example_plugin/pyproject.toml`).
- At runtime Jusu discovers installed plugins via `arpah.discover_plugins()`.

Quick local demo (without installing):

```python
from runtime import arpah
import sys
sys.path.insert(0, 'examples/example_plugin')
from example_plugin import plugin
arpah.register_builtin('example', plugin.load())
plugins = arpah.discover_plugins()
print(plugins['example'].hello())  # 'hello from example plugin'
```

## Tips
- Prefer WASM for untrusted native modules.
- Wrap powerful foreign calls in `runtime.sandbox` when running user-supplied code.
- Use `tools/init_jusu_package.py` to scaffold a plugin package.
