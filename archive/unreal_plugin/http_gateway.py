#!/usr/bin/env python3
"""Simple HTTP gateway that wraps the Jusu++ bridge behavior without extra dependencies.
POST /run accepts JSON with keys: cmd (run_script, run_script_path), script or script_path, auth_token (optional), timeout, backend.
"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import argparse
from pathlib import Path
import urllib.parse
from runtime import sandbox
import sys

class RunHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != '/run':
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get('content-length', '0'))
        raw = self.rfile.read(length)
        try:
            req = json.loads(raw.decode('utf-8'))
        except Exception as e:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': 'invalid json', 'detail': str(e)}).encode('utf-8'))
            return
        # optional auth check
        auth_token = getattr(self.server, 'auth_token', None)
        if auth_token:
            provided = req.get('auth_token') or req.get('token')
            if provided != auth_token:
                self.send_response(401)
                self.end_headers()
                self.wfile.write(json.dumps({'ok': False, 'error': 'unauthorized'}).encode('utf-8'))
                return
        cmd = req.get('cmd')
        if cmd == 'run_script' or cmd == 'run_script_path':
            if cmd == 'run_script':
                src = req.get('script', '')
                if not src:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(json.dumps({'ok': False, 'error': 'empty script'}).encode('utf-8'))
                    return
                res = sandbox.run_source(src, timeout=req.get('timeout', 5), memory_limit_mb=req.get('mem'), backend=req.get('backend', 'interp'))
            else:
                path = req.get('script_path')
                if not path or not Path(path).exists():
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(json.dumps({'ok': False, 'error': 'script_path not found'}).encode('utf-8'))
                    return
                res = sandbox.run_file(path, timeout=req.get('timeout', 5), memory_limit_mb=req.get('mem'), backend=req.get('backend', 'interp'))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(res).encode('utf-8'))
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': 'unknown cmd'}).encode('utf-8'))


def main(port: int = 8777, host: str = '127.0.0.1', auth_token: str = None):
    server = HTTPServer((host, port), RunHandler)
    server.auth_token = auth_token
    print(f'HTTP gateway listening on http://{host}:{port}/run (auth={"enabled" if auth_token else "disabled"})')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Shutdown')
        server.shutdown()


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--port', type=int, default=8777)
    p.add_argument('--host', default='127.0.0.1')
    p.add_argument('--auth-token', default=None)
    args = p.parse_args()
    main(port=args.port, host=args.host, auth_token=args.auth_token)
