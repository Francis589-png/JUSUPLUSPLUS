#!/usr/bin/env python3
"""Jusu++ <-> Unreal bridge (JSON over TCP)

Simple bridge for prototyping: listens for JSON requests and runs Jusu++ scripts.
Request format (JSON line):
  { "cmd": "run_script", "script": "<script contents>" }
  or
  { "cmd": "run_script_path", "script_path": "<path>" }
Response format (JSON line):
  { "ok": true, "stdout": "...", "stderr": "...", "returncode": 0 }

Security note: this executes arbitrary Jusu++ code; run only in trusted or sandboxed environments.
"""
import argparse
import json
import socketserver
import tempfile
import subprocess
import sys
from pathlib import Path

class JSONTCPHandler(socketserver.StreamRequestHandler):
    def handle(self):
        for line in self.rfile:
            try:
                req = json.loads(line.decode('utf-8'))
            except Exception as e:
                self.wfile.write(json.dumps({'ok': False, 'error': 'invalid json', 'detail': str(e)}).encode('utf-8') + b"\n")
                continue
            # optional auth token check
            auth_token = getattr(self.server, 'auth_token', None)
            if auth_token:
                provided = req.get('auth_token') or req.get('token')
                if provided != auth_token:
                    self.wfile.write(json.dumps({'ok': False, 'error': 'unauthorized'}).encode('utf-8') + b"\n")
                    continue
            cmd = req.get('cmd')
            if cmd == 'run_script' or cmd == 'run_script_path':
                if cmd == 'run_script':
                    script = req.get('script', '')
                    if not script:
                        self.wfile.write(json.dumps({'ok': False, 'error': 'empty script'}).encode('utf-8') + b"\n")
                        continue
                    tmpf = tempfile.NamedTemporaryFile(prefix='jusu_', suffix='.jusu', delete=False)
                    tmpf.write(script.encode('utf-8'))
                    tmpf.flush()
                    tmpf.close()
                    path = tmpf.name
                else:
                    path = req.get('script_path')
                    if not path or not Path(path).exists():
                        self.wfile.write(json.dumps({'ok': False, 'error': 'script_path not found'}).encode('utf-8') + b"\n")
                        continue
                # run the script via sandbox if enabled, otherwise subprocess
                try:
                    if getattr(self.server, 'use_sandbox', False):
                        from runtime import sandbox
                        mem = getattr(self.server, 'memory_limit_mb', None)
                        result = sandbox.run_file(path, timeout=req.get('timeout', 5), memory_limit_mb=mem, backend=req.get('backend', 'interp'))
                        resp = {
                            'ok': True if result.get('returncode') == 0 and not result.get('timed_out') else False,
                            'stdout': result.get('stdout', ''),
                            'stderr': result.get('stderr', ''),
                            'returncode': result.get('returncode'),
                            'timed_out': result.get('timed_out', False),
                            'killed': result.get('killed', False),
                        }
                    else:
                        proc = subprocess.run([sys.executable, 'compiler/jusu.py', 'run', str(path)], capture_output=True, text=True, timeout=req.get('timeout', 5))
                        resp = {'ok': True, 'stdout': proc.stdout, 'stderr': proc.stderr, 'returncode': proc.returncode}
                except subprocess.TimeoutExpired:
                    resp = {'ok': False, 'error': 'timeout'}
                except Exception as e:
                    resp = {'ok': False, 'error': 'exception', 'detail': str(e)}
                self.wfile.write(json.dumps(resp).encode('utf-8') + b"\n")
            else:
                self.wfile.write(json.dumps({'ok': False, 'error': 'unknown cmd'}).encode('utf-8') + b"\n")


def main(port: int = 8765, host: str = '127.0.0.1', auth_token: str = None, tls_cert: str = None, tls_key: str = None, use_sandbox: bool = False, memory_limit_mb: int = None):
    server = socketserver.ThreadingTCPServer((host, port), JSONTCPHandler)
    # attach auth token (None means no auth required)
    server.auth_token = auth_token
    server.use_sandbox = use_sandbox
    server.memory_limit_mb = memory_limit_mb
    # optional TLS wrapping
    if tls_cert and tls_key:
        try:
            import ssl
            server.socket = ssl.wrap_socket(server.socket, server_side=True, certfile=tls_cert, keyfile=tls_key)
            print('TLS enabled on bridge')
        except Exception as e:
            print('Failed to enable TLS:', e)
    print(f'Jusu++ Unreal Bridge listening on {host}:{port} (auth={"enabled" if auth_token else "disabled"} sandbox={"enabled" if use_sandbox else "disabled"})')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Shutting down')
        server.shutdown()


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--port', type=int, default=8765)
    p.add_argument('--host', default='127.0.0.1')
    p.add_argument('--auth-token', default=None, help='Optional auth token required in each request as auth_token')
    p.add_argument('--tls-cert', default=None, help='Optional TLS cert file path')
    p.add_argument('--tls-key', default=None, help='Optional TLS key file path')
    p.add_argument('--use-sandbox', action='store_true', help='Run scripts via the sandbox runner')
    p.add_argument('--mem-limit', type=int, default=None, help='Optional memory limit in MB for sandboxed runs')
    args = p.parse_args()
    main(port=args.port, host=args.host, auth_token=args.auth_token, tls_cert=args.tls_cert, tls_key=args.tls_key, use_sandbox=args.use_sandbox, memory_limit_mb=args.mem_limit)

