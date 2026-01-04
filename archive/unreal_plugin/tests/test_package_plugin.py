import subprocess
import sys
from pathlib import Path

SCRIPT = Path('projects') / 'unreal_plugin' / 'tools' / 'package_unreal_plugin.py'
OUT = Path('projects') / 'unreal_plugin' / 'artifacts' / 'unreal_example_plugin.zip'


def test_package_creates_zip(tmp_path):
    # run packaging into tmp dir
    r = subprocess.run([sys.executable, str(SCRIPT), '--out', str(tmp_path)], capture_output=True, text=True)
    # expect zip file at tmp_path/unreal_example_plugin.zip
    z = tmp_path / 'unreal_example_plugin.zip'
    assert z.exists(), f'package not created; stdout: {r.stdout} stderr: {r.stderr}'
