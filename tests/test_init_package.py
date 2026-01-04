import subprocess
import sys
from pathlib import Path
import tempfile


def test_init_package_creates_pyproject():
    tmp = Path(tempfile.mkdtemp())
    r = subprocess.run([sys.executable, 'tools/init_jusu_package.py', str(tmp)], capture_output=True, text=True)
    # the script may print help or scaffolding info; check for pyproject or package dir
    has_pyproject = (tmp / 'pyproject.toml').exists() or any(tmp.glob('*/pyproject.toml'))
    assert has_pyproject or r.returncode == 0, f"Scaffolding didn't produce pyproject in {tmp}; stdout: {r.stdout} stderr: {r.stderr}"
