"""
Minimal Data Science module for Jusu++
- Uses NumPy if available (recommended)
- Falls back to pure-Python implementations for basic operations

Exports a simple module-like object with methods:
- array(seq)
- sum(seq)
- mean(seq)
- dot(a, b)
- matmul(a, b)
- shape(a)
"""

try:
    import numpy as _np
    HAS_NUMPY = True
except Exception:
    _np = None
    HAS_NUMPY = False

try:
    import pandas as _pd
    HAS_PANDAS = True
except Exception:
    _pd = None
    HAS_PANDAS = False

class DataScienceModule:
    def array(self, x):
        if HAS_NUMPY:
            return _np.array(x)
        # fallback: keep Python lists
        return list(x)

    def sum(self, seq):
        if HAS_NUMPY:
            return _np.sum(seq).tolist()
        # accept list-like
        s = 0
        for v in seq:
            s += v
        return s

    def mean(self, seq):
        if HAS_NUMPY:
            return float(_np.mean(seq))
        seq = list(seq)
        return sum(seq) / len(seq) if seq else 0

    def dot(self, a, b):
        if HAS_NUMPY:
            return _np.dot(a, b).tolist() if hasattr(_np.dot(a,b), 'tolist') else _np.dot(a,b)
        # fallback: simple 1D dot
        return sum(x*y for x,y in zip(a,b))

    def matmul(self, a, b):
        if HAS_NUMPY:
            return _np.matmul(a, b).tolist()
        # fallback: naive matrix multiply
        # assume a: list of rows, b: list of rows -> convert b columns
        b_cols = list(zip(*b))
        result = []
        for row in a:
            result.append([sum(x*y for x,y in zip(row, col)) for col in b_cols])
        return result

    def shape(self, a):
        if HAS_NUMPY:
            return tuple(_np.array(a).shape)
        if isinstance(a, list):
            if not a:
                return (0,)
            if isinstance(a[0], list):
                return (len(a), len(a[0]))
            return (len(a),)
        return ()

    def __repr__(self):
        parts = [f"numpy={'yes' if HAS_NUMPY else 'no'}"]
        parts.append(f"pandas={'yes' if HAS_PANDAS else 'no'}")
        return f"<DataScienceModule {' '.join(parts)}>"


class PandasModule:
    """Thin wrapper exposing a couple of pandas conveniences when pandas present."""
    def read_csv(self, *args, **kwargs):
        if not HAS_PANDAS:
            raise RuntimeError("pandas not available")
        return _pd.read_csv(*args, **kwargs)

    def DataFrame(self, data, *args, **kwargs):
        if not HAS_PANDAS:
            raise RuntimeError("pandas not available")
        return _pd.DataFrame(data, *args, **kwargs)

    def __repr__(self):
        return f"<PandasModule pandas={'yes' if HAS_PANDAS else 'no'}>"
