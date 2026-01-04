import pytest

try:
    from runtime import wasm
    HAS_WASM = wasm.available()
except Exception:
    HAS_WASM = False


@pytest.mark.skipif(not HAS_WASM, reason="wasmtime not installed")
def test_instantiate_wat_and_call_add():
    # WAT for: (module (func (export "add") (param i32 i32) (result i32) local.get 0 local.get 1 i32.add))
    wat = """
    (module
      (func $add (param $a i32) (param $b i32) (result i32)
        local.get $a
        local.get $b
        i32.add)
      (export "add" (func $add)))
    """
    inst = wasm.instantiate_wat(wat)
    res = inst.call('add', 3, 4)
    assert res == 7
