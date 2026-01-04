"""Core Automation Agent

Discover plugins in projects/automation_agent/plugins and run them.
"""
from pathlib import Path
import importlib.util
import sys
from typing import Dict, Callable

PLUGINS_DIR = Path(__file__).resolve().parent / 'plugins'


class Agent:
    def __init__(self, plugins_dir: Path = PLUGINS_DIR):
        self.plugins_dir = Path(plugins_dir)
        self.plugins: Dict[str, Callable] = {}

    def discover(self):
        self.plugins.clear()
        if not self.plugins_dir.exists():
            return
        for p in self.plugins_dir.glob('*.py'):
            if p.name.startswith('_'):
                continue
            name = p.stem
            spec = importlib.util.spec_from_file_location(name, str(p))
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)  # type: ignore
            except Exception as e:
                # Skip plugins that error at import
                print(f"Skipping plugin {name}: import failed: {e}")
                continue
            # require plugin contract
            plugin_name = getattr(module, 'name', None) or name
            run = getattr(module, 'run', None)
            if callable(run):
                self.plugins[plugin_name] = run

    def run_plugin(self, plugin_name: str, context: dict) -> dict:
        if plugin_name not in self.plugins:
            raise KeyError(plugin_name)
        fn = self.plugins[plugin_name]
        return fn(context)

    def run_all(self, context: dict = None) -> dict:
        context = context or {}
        results = {}
        for name, fn in self.plugins.items():
            try:
                results[name] = fn(context)
            except Exception as e:
                results[name] = {'error': str(e)}
        return results
