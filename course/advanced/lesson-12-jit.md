# Lesson 12 — LLVM JIT Basics & `llvmlite` ⚡️

## Objectives
- Understand the JIT pipeline used in Jusu++
- Write a small numeric function and compile it with `llvmlite`
- Benchmark interpreter vs. JIT for hot functions

## Lab
- Explore `runtime/jit.py` and `tools/jit_benchmark.py`.
- Run benchmark with: `python tools/jit_benchmark.py` (requires `llvmlite`).

## Exercises
- Extend JIT to handle a simple binary-op expression tree and add tests.
- Measure performance and report speedups.
