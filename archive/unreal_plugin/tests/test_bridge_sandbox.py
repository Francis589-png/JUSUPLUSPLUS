import subprocess
import sys
import socket
import json
import time
import os
import pytest
from pathlib import Path

BRIDGE = Path('projects') / 'unreal_plugin' / 'jusu_unreal_bridge.py'

SKIP_WINDOWS = sys.platform.startswith('win')


def test_bridge_sandbox_timeout():
    if SKIP_WINDOWS:
        pytest.skip('Sandbox timeout behavior is platform dependent on Windows')
    proc = subprocess.Popen([sys.executable, str(BRIDGE), '--port', '8892', '--use-sandbox'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        time.sleep(0.5)
        s = socket.create_connection(('127.0.0.1', 8892), timeout=2)
        # busy loop script
        script = 'while (1) { x = 1 }'
        req = {'cmd': 'run_script', 'script': script, 'timeout': 1}
        s.sendall((json.dumps(req) + '\n').encode('utf-8'))
        data = s.recv(8192)
        s.close()
        resp = json.loads(data.decode('utf-8'))
        assert not resp.get('ok')
        assert resp.get('timed_out') is True
    finally:
        proc.terminate()
        proc.wait(timeout=2)
