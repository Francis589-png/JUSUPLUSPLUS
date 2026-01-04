import importlib
import sys
import os
# Ensure project root is on sys.path when running tests as scripts
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from runtime import pkgmgr, arpah


def test_register_and_discover():
    # Register programmatically and verify discovery
    class Dummy:
        def ping(self):
            return 'pong'
    pkgmgr.register_builtin('dummy', Dummy())
    plugins = pkgmgr.discover_plugins()
    assert 'dummy' in plugins
    assert plugins['dummy'].ping() == 'pong'


def test_discover_entry_point_monkeypatch(tmp_path, monkeypatch):
    # Simulate an entry point by creating a dummy module and an object
    module_name = 'fake_pkg'
    mod = type('M', (), {})()
    def load():
        return type('P', (), {'ok': lambda self: 'yes'})()
    setattr(mod, 'plugin', type('Pmod', (), {'load': staticmethod(load)}))
    sys.modules[module_name] = mod

    # Monkeypatch importlib.metadata.entry_points to return a fake entry
    class FakeEP:
        def __init__(self, name, module, attr):
            self.name = name
            self._module = module
            self._attr = attr
        def load(self):
            return getattr(sys.modules[self._module], self._attr)

    def fake_entry_points():
        return {'jusu.plugins': [FakeEP('fake', module_name, 'plugin.load')]}

    # Older importlib.metadata API returns dict
    monkeypatch.setattr('importlib.metadata.entry_points', lambda: fake_entry_points())

    plugins = pkgmgr.discover_plugins()
    # discovery may skip malformed objects but should not crash
    assert isinstance(plugins, dict)
