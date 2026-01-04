"""Sandbox runner for executing Jusu programs with timeout and optional memory limit.

API:
- run_file(path, timeout=5, memory_limit_mb=None, backend='interp') -> result dict
  result contains: returncode, stdout, stderr, timed_out (bool), killed (bool)

This implementation launches a subprocess running `python -m runtime._sandbox_child`.
"""
from __future__ import annotations

import sys
import subprocess
import tempfile
import os
from typing import Optional, Dict, Any


def run_file(path: str, timeout: float = 5.0, memory_limit_mb: Optional[int] = None, backend: str = 'interp') -> Dict[str, Any]:
    cmd = [sys.executable, '-u', '-m', 'runtime._sandbox_child', '--file', path, '--backend', backend]
    if memory_limit_mb:
        cmd += ['--mem', str(int(memory_limit_mb))]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {
            'returncode': proc.returncode,
            'stdout': proc.stdout,
            'stderr': proc.stderr,
            'timed_out': False,
            'killed': False,
        }
    except subprocess.TimeoutExpired as e:
        # Process exceeded time; we attempted to kill it via subprocess.run
        # however TimeoutExpired doesn't guarantee the process died; mark timed_out=True
        out = (e.stdout or '')
        err = (e.stderr or '')
        return {
            'returncode': None,
            'stdout': out,
            'stderr': err,
            'timed_out': True,
            'killed': True,
        }
    except Exception as e:
        return {
            'returncode': None,
            'stdout': '',
            'stderr': str(e),
            'timed_out': False,
            'killed': False,
        }


def run_source(src: str, timeout: float = 5.0, memory_limit_mb: Optional[int] = None, backend: str = 'interp') -> Dict[str, Any]:
    # Write to a temporary file and run
    with tempfile.NamedTemporaryFile('w', suffix='.jusu', delete=False) as f:
        f.write(src)
        tmp = f.name
    try:
        return run_file(tmp, timeout=timeout, memory_limit_mb=memory_limit_mb, backend=backend)
    finally:
        try:
            os.unlink(tmp)
        except Exception:
            pass
