import os
import sys
import shutil
import tempfile

# Ensure project root on sys.path when running tests directly
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from runtime import js
import pytest


@pytest.mark.skipif(not js.AVAILABLE, reason="node not available")
def test_js_call_local_script():
    # Create a temp JS module exporting a function
    fd, p = tempfile.mkstemp(suffix='.js')
    os.close(fd)
    with open(p, 'w') as f:
        f.write("module.exports = { add: (a,b) => a + b, asyncAdd: async (a,b) => a + b };\n")

    res = js.call(p, 'add', [3, 4])
    assert res == 7

    res2 = js.call(p, 'asyncAdd', [5, 6])
    assert res2 == 11

    os.unlink(p)
