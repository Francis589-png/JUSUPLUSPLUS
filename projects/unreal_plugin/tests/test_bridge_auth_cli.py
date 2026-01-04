import subprocess
import sys
from pathlib import Path

BRIDGE = Path('projects') / 'unreal_plugin' / 'jusu_unreal_bridge.py'


def test_bridge_cli_accepts_args():
    r = subprocess.run([sys.executable, str(BRIDGE), '--help'], capture_output=True, text=True)
    assert r.returncode == 0
    assert '--auth-token' in r.stdout or '--auth-token' in r.stderr
