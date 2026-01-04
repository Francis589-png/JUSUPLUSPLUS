"""Run all test files in the workspace's tests/ directory using the active venv python."""
import glob
import subprocess
import sys

files = sorted(glob.glob('tests/*.py'))
if not files:
    print('No tests found')
    sys.exit(0)

for f in files:
    print('--- RUN', f)
    r = subprocess.run([sys.executable, f])
    if r.returncode != 0:
        print('Test failed:', f)
        sys.exit(r.returncode)

print('All tests passed')
