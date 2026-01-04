"""
Simple helper to generate a course index (markdown) by scanning the course folder.
Run: python course/tools/generate_course_index.py
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "course" / "generated_index.md"

def scan():
    parts = [p.relative_to(ROOT) for p in (ROOT / "beginner").glob("**/*.md")]
    with OUT.open("w", encoding="utf-8") as f:
        f.write("# Generated Course Index\n\n")
        for p in sorted(parts):
            f.write(f"- [{p.name}]({p.as_posix()})\n")

if __name__ == '__main__':
    scan()
    print("Generated index at", OUT)
