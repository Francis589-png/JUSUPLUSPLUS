"""Node.js bridge for Jusu++

Provides a thin RPC-style bridge to call Node.js modules/functions from Jusu.
- Uses `node` executable if available (checked at import time).
- call(module_path_or_name, func_name, args, timeout=5.0) -> Python value

Security note: running untrusted JS code invokes node and executes real JS —
use sandbox.run_file to execute user programs with time/memory limits when needed.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import os
from typing import Any, List, Optional

HAS_NODE = shutil.which('node') is not None


class JSBridgeError(RuntimeError):
    pass


_NODE_RUNNER = r"""
// Simple runner: node - <module> <func>
// Reads JSON array from stdin as function args and writes JSON to stdout
const [modPath, funcName] = process.argv.slice(1);
let mod;
try {
    mod = require(modPath);
} catch (e) {
    console.error(JSON.stringify({error: String(e)}));
    process.exit(2);
}
const fs = require('fs');
let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (c) => input += c);
process.stdin.on('end', async () => {
    try {
        const args = JSON.parse(input || '[]');
        const fn = mod[funcName];
        if (typeof fn !== 'function') {
            console.error(JSON.stringify({error: 'Function not found'}));
            process.exit(3);
        }
        let res = fn(...args);
        if (res && typeof res.then === 'function') res = await res;
        console.log(JSON.stringify({result: res}));
    } catch (e) {
        console.error(JSON.stringify({error: String(e)}));
        process.exit(4);
    }
});
""".lstrip()


def _node_available() -> bool:
    return HAS_NODE


def call(module: str, func: str, args: Optional[List[Any]] = None, timeout: float = 5.0) -> Any:
    """Call `func` exported by `module` (path or module name).

    If `module` is a relative/absolute path to a .js file, it will be resolved directly.
    Otherwise it is passed to `require()` (so Node's module resolution applies).
    Returns the deserialized JSON `result` or raises `JSBridgeError` on errors.
    """
    if not _node_available():
        raise JSBridgeError('node is not installed or not on PATH')
    if args is None:
        args = []

    # Resolve module path to absolute if looks like a file
    if module.endswith('.js') or module.startswith('./') or module.startswith('/') or module.startswith('\\'):
        module_path = os.path.abspath(module)
    else:
        module_path = module

    # Launch node with runner via stdin (use -e to execute code?) We'll pass the runner via stdin to 'node -' and args
    # Simpler: use `node -` and prepend the runner code, then pass module and func as argv
    cmd = [shutil.which('node'), '-']
    try:
        proc = subprocess.run(cmd, input=_NODE_RUNNER + '\n', text=True, capture_output=True, timeout=timeout, args=(module_path, func))
        # NOTE: subprocess.run doesn't accept args positional like this when passing input; instead we'll compose the argv differently
    except TypeError:
        # older Python: run without args param, instead add module and func to command and use -e with script
        pass

    # Compose a command that invokes node with the runner script via -e and module/func as argv; pass JSON args on stdin
    cmd = [shutil.which('node'), '-e', _NODE_RUNNER, module_path, func]
    try:
        p = subprocess.run(cmd, input=json.dumps(args), text=True, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired as e:
        raise JSBridgeError('Node call timed out')

    out = p.stdout.strip()
    err = p.stderr.strip()

    # If stderr contains JSON error, try to parse it
    if p.returncode != 0:
        try:
            j = json.loads(err or out or '{}')
            if 'error' in j:
                raise JSBridgeError(f"JS error: {j['error']}")
        except Exception:
            raise JSBridgeError(f"Node process failed (code {p.returncode}): {err}")

    # Parse stdout
    try:
        j = json.loads(out)
    except Exception as e:
        raise JSBridgeError(f"Failed to parse Node output: {e}; stdout={out}; stderr={err}")

    if 'error' in j:
        raise JSBridgeError(f"JS error: {j['error']}")
    return j.get('result')


# Convenience: check availability at import time
AVAILABLE = _node_available()
