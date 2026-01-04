#!/usr/bin/env python3
"""Simple helper to bump the project version in pyproject.toml and create a tag.
Usage: python tools/release.py <new-version>

This is intentionally minimal — it edits [project].version key and commits the change.
"""
import sys
from pathlib import Path
import re

if len(sys.argv) < 2:
    print('Usage: python tools/release.py <new-version>')
    sys.exit(1)

v = sys.argv[1]
py = Path('pyproject.toml')
if not py.exists():
    print('pyproject.toml not found')
    sys.exit(1)

s = py.read_text()
new, n = re.subn(r'(version\s*=\s*")([^"]+)(")', r'\1' + v + r'\3', s)
if n == 0:
    print('version key not found in pyproject.toml')
    sys.exit(1)
py.write_text(new)
print(f'Bumped version to {v} in pyproject.toml')

# Commit and tag
import subprocess
subprocess.check_call(['git', 'add', 'pyproject.toml', 'CHANGES.md'])
subprocess.check_call(['git', 'commit', '-m', f'Bump version to {v}'])
subprocess.check_call(['git', 'tag', '-a', f'v{v}', '-m', f'Release v{v}'])
print('Committed and created tag. Push with `git push --follow-tags` to publish.')
