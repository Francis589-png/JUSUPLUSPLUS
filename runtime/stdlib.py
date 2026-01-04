"""
Jusu++ Standard Library (minimal)
Expose simple modules: math, json, time, random and helpers.
get_builtins() returns a mapping of names to module-like dicts or callables.
"""
import math
import json
import time
import random

class MathModule:
    pi = math.pi
    def sqrt(self, x):
        return math.sqrt(x)
    def sin(self, x):
        return math.sin(x)

class JSONModule:
    def loads(self, s):
        return json.loads(s)
    def dumps(self, obj):
        return json.dumps(obj)

class TimeModule:
    def now(self):
        return time.time()

class RandomModule:
    def rand(self):
        return random.random()

def get_builtins():
    # Import datascience lazily to avoid hard dependency on numpy/pandas
    try:
        from runtime.datascience import DataScienceModule, PandasModule
        ds = DataScienceModule()
        pd_mod = PandasModule()
    except Exception:
        ds = None
        pd_mod = None

    builtins = {
        'math': MathModule(),
        'json': JSONModule(),
        'time': TimeModule(),
        'random': RandomModule(),
        'http': __import__('runtime.web', fromlist=['WebModule']).WebModule(),
        'ffi': __import__('runtime.ffi', fromlist=['load']).load,
        'js': __import__('runtime.js', fromlist=['call']) ,
        'wasm': __import__('runtime.wasm', fromlist=['instantiate_wat']) ,
    }

    # Always expose 'np' with the provided wrapper (fallback works when numpy missing)
    if ds is not None:
        builtins['np'] = ds

    # Expose 'pd' if pandas wrapper present; otherwise provide a lightweight stub
    if pd_mod is not None:
        builtins['pd'] = pd_mod
    else:
        class _PandasMissingStub:
            def __getattr__(self, name):
                raise RuntimeError("pandas not available; install via 'pip install pandas' to use pd.* features")
            def __repr__(self):
                return "<PandasModule pandas=no>"
        builtins['pd'] = _PandasMissingStub()

    # Discover external plugins (third-party packages) and inject them
    try:
        from runtime import pkgmgr
        plugins = pkgmgr.discover_plugins()
        builtins.update(plugins)
    except Exception:
        # noop if plugin manager missing or discovery fails
        pass

    return builtins
