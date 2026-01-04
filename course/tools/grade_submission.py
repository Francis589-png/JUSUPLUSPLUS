"""Grade a student submission.

Expect submission layout: course/submissions/<lesson>/<student>/
Each submission must provide a `run.sh` or `run.py` that prints PASS on success.
The grader runs the script and returns a JSON with {passed: bool, output: str}
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def grade_submission(sub_path: Path):
    sub_path = Path(sub_path)
    if not sub_path.exists():
        raise SystemExit(f"Submission not found: {sub_path}")
    runner_py = sub_path / 'run.py'
    runner_sh = sub_path / 'run.sh'
    if runner_py.exists():
        proc = subprocess.run([sys.executable, str(runner_py)], capture_output=True, text=True)
    elif runner_sh.exists():
        proc = subprocess.run(['bash', str(runner_sh)], capture_output=True, text=True)
    else:
        return {'passed': False, 'output': 'No runner found'}
    out = proc.stdout + '\n' + proc.stderr
    passed = 'PASS' in proc.stdout
    return {'passed': passed, 'output': out, 'returncode': proc.returncode}


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python course/tools/grade_submission.py <submission_dir>')
        raise SystemExit(2)
    path = Path(sys.argv[1])
    print(json.dumps(grade_submission(path), indent=2))
