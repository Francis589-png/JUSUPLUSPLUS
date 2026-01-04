import subprocess
import sys
import socket
import json
import time
from pathlib import Path

BRIDGE = Path('projects') / 'unreal_plugin' / 'jusu_unreal_bridge.py'
EXAMPLE_SCRIPT = Path('projects') / 'unreal_plugin' / 'examples' / 'platformer.jusu'


def test_bridge_runs_and_executes_example(tmp_path):
    assert BRIDGE.exists()
    # start bridge as a background process
    proc = subprocess.Popen([sys.executable, str(BRIDGE), '--port', '8888'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        time.sleep(0.5)
        # connect via socket and send run_script_path
        s = socket.create_connection(('127.0.0.1', 8888), timeout=2)
        req = {'cmd': 'run_script_path', 'script_path': str(EXAMPLE_SCRIPT)}
        s.sendall((json.dumps(req) + '\n').encode('utf-8'))
        data = s.recv(8192)
        s.close()
        resp = json.loads(data.decode('utf-8'))
        assert resp['ok']
        assert 'enemy' in resp['stdout'] or resp['returncode'] == 0
    finally:
        proc.terminate()
        proc.wait(timeout=2)
