import pytest

try:
    import pandas as pd
    HAS_PANDAS = True
except Exception:
    HAS_PANDAS = False


@pytest.mark.skipif(not HAS_PANDAS, reason="pandas not available")
def test_pandas_module_in_stdlib():
    from runtime.stdlib import get_builtins
    builtins = get_builtins()
    assert 'pd' in builtins
    pd_mod = builtins['pd']
    df = pd_mod.DataFrame({'a': [1,2], 'b': [3,4]})
    assert list(df['a']) == [1,2]
