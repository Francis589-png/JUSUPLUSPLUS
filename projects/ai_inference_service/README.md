AI Inference Service (Demo)

This demo shows a minimal inference pipeline where a lightweight Python "model" is wrapped by a simple service.
It demonstrates how Jusu++ can orchestrate model calls (via subprocess/Python), serve predictions, and be tested/benchmarked.

Files:
- `predict.py` — a tiny Python prediction stub that accepts JSON input on stdin and writes JSON output.
- `tests/test_predict.py` — test that runs the predictor and validates output.

Usage (demo):
- python projects/ai_inference_service/predict.py '{"x": 3}'
- Expected output: JSON with a `prediction` key.

Notes:
- Replace `predict.py` with a model wrapper (PyTorch/TensorFlow) in production.
- For model serving, integrate with a web framework or use the `http` module from the stdlib.
