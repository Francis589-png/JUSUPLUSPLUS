# Contributing to Jusu++

Thanks for contributing! This document explains how to set up the dev
environment, run tests, and submit patches.

Getting started
- Create a virtual environment: `python -m venv .venv && . .venv/Scripts/Activate.ps1` (Windows) or `source .venv/bin/activate` (Unix).
- Install dev extras: `pip install -e '.[dev]'

Run tests
- Use the helper: `python tools/run_tests.py` (runs all tests).
- To run a single test: `pytest tests/test_foo.py::test_bar -q`.

Code style
- We use `black` and `flake8`. Pre-commit is configured; run `pre-commit install`.

Publishing plugins
- Use `tools/init_jusu_package.py <name>` to scaffold a plugin package.
- Publish to PyPI/TestPyPI; ensure your package declares an entry point in `jusu.plugins`.

Security and sandboxing
- Ensure any code that executes third-party native modules is run inside the sandbox runner (`runtime.sandbox`) or otherwise properly isolated.

Thank you!
