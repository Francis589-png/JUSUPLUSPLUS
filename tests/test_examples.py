import os
import sys
import importlib

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from runtime import arpah


def test_example_plugin_registration():
    # Use local examples/example_plugin by adding it to sys.path
    pkg_path = os.path.join(ROOT, 'examples', 'example_plugin')
    assert os.path.exists(pkg_path)
    if pkg_path not in sys.path:
        sys.path.insert(0, pkg_path)
    mod = importlib.import_module('example_plugin.plugin')
    arpah.register_builtin('example_demo', mod.load())
    plugins = arpah.discover_plugins()
    assert 'example_demo' in plugins
    assert plugins['example_demo'].hello() == 'hello from example plugin'
