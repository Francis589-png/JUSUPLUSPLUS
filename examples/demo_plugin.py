"""Demo: load example plugin locally without installing and register via arpah."""
import sys
import os
ROOT = os.path.abspath(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from runtime import arpah

# Import plugin module directly
from example_plugin import plugin
mod = plugin.load()
arpah.register_builtin('example', mod)

# Use it
plugins = arpah.discover_plugins()
print('discovered:', 'example' in plugins)
print('hello:', plugins['example'].hello())
print('add:', plugins['example'].add(3,4))
