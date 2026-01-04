import subprocess
import sys
import json
from pathlib import Path

SCRIPT = Path('projects') / 'ai_inference_service' / 'predict.py'


def test_predict_cli():
    assert SCRIPT.exists()
    r = subprocess.run([sys.executable, str(SCRIPT), json.dumps({'x': 4})], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    j = json.loads(r.stdout)
    assert j['prediction'] == 2 * 4 + 1
