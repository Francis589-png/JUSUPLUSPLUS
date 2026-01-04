# Lesson 01 — Introduction to Jusu++ 🎉

## Objectives
- Understand Jusu++ goals and use-cases
- Install the toolchain and run the REPL
- Write and run your first program

## Setup
1. Clone repository and create virtualenv
   - python -m venv .venv
   - .venv\Scripts\Activate.ps1 (Windows) or source .venv/bin/activate (Unix)
2. Install dev requirements
   - pip install -e .[dev]
3. Run tests
   - python tools/run_tests.py

## First program (hello.jusu)
```jusu
print("Hello, Jusu++!")
```
Run:
- python compiler/jusu.py run examples/hello.jusu
- or enter REPL: python compiler/jusu.py

## Short quiz
- What is the REPL command to run a file?
- Where is the `arpah` package manager located?

## Exercises
1. Modify `examples/hello.jusu` to accept a name and greet it.
2. Add a small program that computes factorial iteratively.

Solutions: see `course/beginner/solutions/lesson-01.md`.
