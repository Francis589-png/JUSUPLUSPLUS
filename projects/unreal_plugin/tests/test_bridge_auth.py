import subprocess
import sys
import socket
import json
import time
from pathlib import Path

BRIDGE = Path('projects') / 'unreal_plugin' / 'jusu_unreal_bridge.py'
EXAMPLE_SCRIPT = Path('projects') / 'unreal_plugin' / 'examples' / 'platformer.jusu'


def test_bridge_auth_accepts_valid_token():
    proc = subprocess.Popen([sys.executable, str(BRIDGE), '--port', '8890', '--auth-token', 'SECRET'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        time.sleep(0.5)
        s = socket.create_connection(('127.0.0.1', 8890), timeout=2)
        req = {'cmd': 'run_script_path', 'script_path': str(EXAMPLE_SCRIPT), 'auth_token': 'SECRET'}
        s.sendall((json.dumps(req) + '\n').encode('utf-8'))
        data = s.recv(8192)
        s.close()
        resp = json.loads(data.decode('utf-8'))
        assert resp['ok']
    finally:
        proc.terminate()
        proc.wait(timeout=2)


def test_bridge_auth_rejects_missing_token():
    proc = subprocess.Popen([sys.executable, str(BRIDGE), '--port', '8891', '--auth-token', 'SECRET2'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        time.sleep(0.5)
        s = socket.create_connection(('127.0.0.1', 8891), timeout=2)
        req = {'cmd': 'run_script_path', 'script_path': str(EXAMPLE_SCRIPT)}
        s.sendall((json.dumps(req) + '\n').encode('utf-8'))
        data = s.recv(8192)
        s.close()
        resp = json.loads(data.decode('utf-8'))
        assert not resp.get('ok')
        assert resp.get('error') == 'unauthorized'
    finally:
        proc.terminate()
        proc.wait(timeout=2)
