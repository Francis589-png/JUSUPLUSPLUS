# WASM runtime (optional)

Jusu++ can call WebAssembly modules via the optional `wasmtime` Python
package. This is useful for portable, sandboxable native code interop.

Quick usage example (from Python tooling):

```python
from runtime import wasm
if not wasm.available():
    print('wasmtime not installed')
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

Notes
- The wasmtime dependency is optional; tests are skipped when not available.
- For security, prefer running unknown Wasm modules inside the sandbox runner.
