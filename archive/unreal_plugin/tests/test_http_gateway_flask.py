import subprocess
import sys
import time
import json
import http.client
import importlib
from pathlib import Path

GATE = Path('projects') / 'unreal_plugin' / 'http_gateway_flask.py'
EXAMPLE_SCRIPT = Path('projects') / 'unreal_plugin' / 'examples' / 'platformer.jusu'


def test_flask_gateway_available():
    try:
        importlib.import_module('flask')
    except Exception:
        import pytest
        pytest.skip('Flask not installed')

    proc = subprocess.Popen([sys.executable, str(GATE), '--port', '8890'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        # Wait for server to be ready with retries
        deadline = time.time() + 5.0
        conn = None
        while time.time() < deadline:
            try:
                conn = http.client.HTTPConnection('127.0.0.1', 8890, timeout=2)
                conn.request('POST', '/run', body=json.dumps({'cmd': 'run_script_path', 'script_path': str(EXAMPLE_SCRIPT)}), headers={'Content-Type': 'application/json'})
                resp = conn.getresponse()
                break
            except Exception:
                time.sleep(0.2)
        assert conn is not None, 'Failed to connect to Flask gateway'
        assert resp.status == 200
        j = json.loads(resp.read().decode('utf-8'))
        assert 'stdout' in j
    finally:
        proc.terminate()
        proc.wait(timeout=2)
