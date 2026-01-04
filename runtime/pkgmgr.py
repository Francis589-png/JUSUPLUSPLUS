"""Package / plugin manager for Jusu++

Plugins are discovered via entry points group `jusu.plugins` (recommended) or
can be programmatically registered via `register_builtin(name, obj)`.

A plugin should expose a module-level factory that returns a module-like
object (for example, a class instance with methods and attributes).

Example pyproject snippet for a plugin package:

[project.entry-points]
"jusu.plugins" = [
    "mypkg = mypkg.plugin:load"
]

The loader should accept no args and return an object to be inserted into
Jusu's builtins under the given name.
"""
from __future__ import annotations

from typing import Dict, Any

_registered: Dict[str, Any] = {}


def register_builtin(name: str, obj: Any):
    """Register an object to be injected into Jusu builtins under `name`."""
    _registered[name] = obj


def discover_plugins() -> Dict[str, Any]:
    """Discover plugins via entry points and include programmatic registrations.

    Returns a mapping name -> object suitable for insertion into builtins.
    """
    plugins: Dict[str, Any] = dict(_registered)

    # Try to load entry points if importlib.metadata is available
    try:
        try:
            # Python 3.10+: entry_points returns Selection
            from importlib.metadata import entry_points
            eps = entry_points()
            group = eps.select(group='jusu.plugins') if hasattr(eps, 'select') else eps.get('jusu.plugins', [])
        except Exception:
            # Fallback older behavior
            from importlib.metadata import entry_points
            group = entry_points().get('jusu.plugins', [])

        for ep in group:
            try:
                name = ep.name
                loader = ep.load()
                # loader can be a callable factory or a module object
                if callable(loader):
                    obj = loader()
                else:
                    obj = loader
                plugins[name] = obj
            except Exception:
                # Skip faulty plugins to keep discovery robust
                continue
    except Exception:
        # importlib.metadata not available or nothing found
        pass

    return plugins
