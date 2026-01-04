"""Arpah: Jusu++ package / plugin manager (formerly pkgmgr)

Provides:
- register_builtin(name, obj)
- discover_plugins() -> dict(name -> object)

Discovery uses entry points in `jusu.plugins` (via importlib.metadata) and
includes programmatic registrations.
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
