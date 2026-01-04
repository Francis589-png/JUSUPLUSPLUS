import subprocess
import sys
from pathlib import Path

def test_notebooks_execute():
    # Skip if nbformat isn't installed
    try:
        import nbformat  # type: ignore
    except Exception:
        import pytest
        pytest.skip('nbformat not installed')

    script = Path('course') / 'tools' / 'execute_notebooks.py'
    assert script.exists(), 'execute_notebooks.py missing'
    r = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    print('stdout:\n', r.stdout)
    print('stderr:\n', r.stderr)
    # Exit code 2 means some notebooks failed; treat non-zero as failure
    assert r.returncode == 0, f'Notebook execution failed with exit code {r.returncode}'
