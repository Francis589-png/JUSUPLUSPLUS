#!/usr/bin/env python3
"""Tiny prediction stub — reads JSON from argv or stdin and returns a JSON prediction."""
import sys
import json

if __name__ == '__main__':
    if len(sys.argv) > 1:
        inp = sys.argv[1]
    else:
        inp = sys.stdin.read() or '{}'
    data = json.loads(inp)
    x = data.get('x', 0)
    # Simple model: prediction = 2*x + 1
    pred = 2 * x + 1
    out = {'prediction': pred}
    print(json.dumps(out))
