#!/usr/bin/env python3
"""Optional Flask-based HTTP gateway for the Jusu++ bridge (requires Flask).
This provides slightly richer error handling and JSON responses compared to the minimal `http_gateway.py`.
"""
from flask import Flask, request, jsonify
import argparse
from pathlib import Path
from runtime import sandbox

app = Flask('jusu_http')

@app.route('/run', methods=['POST'])
def run():
    req = request.get_json(force=True)
    auth_token = getattr(app, 'auth_token', None)
    if auth_token:
        provided = req.get('auth_token') or req.get('token')
        if provided != auth_token:
            return jsonify({'ok': False, 'error': 'unauthorized'}), 401
    cmd = req.get('cmd')
    if cmd == 'run_script':
        src = req.get('script', '')
        if not src:
            return jsonify({'ok': False, 'error': 'empty script'}), 400
        res = sandbox.run_source(src, timeout=req.get('timeout', 5), memory_limit_mb=req.get('mem'), backend=req.get('backend', 'interp'))
        return jsonify(res)
    elif cmd == 'run_script_path':
        path = req.get('script_path')
        if not path or not Path(path).exists():
            return jsonify({'ok': False, 'error': 'script_path not found'}), 400
        res = sandbox.run_file(path, timeout=req.get('timeout', 5), memory_limit_mb=req.get('mem'), backend=req.get('backend', 'interp'))
        return jsonify(res)
    else:
        return jsonify({'ok': False, 'error': 'unknown cmd'}), 400


def main(port: int = 8778, host: str = '127.0.0.1', auth_token: str = None):
    app.auth_token = auth_token
    app.run(host=host, port=port)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--port', type=int, default=8778)
    p.add_argument('--host', default='127.0.0.1')
    p.add_argument('--auth-token', default=None)
    args = p.parse_args()
    main(port=args.port, host=args.host, auth_token=args.auth_token)
