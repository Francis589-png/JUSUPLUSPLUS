from pathlib import Path

def test_exercises_have_solutions():
    root = Path('course')
    exercise_files = list(root.glob('**/exercises/*.md'))
    assert exercise_files, 'No exercise files found'
    missing = []
    for ex in exercise_files:
        sol = ex.parent.parent / 'solutions' / ex.name
        if not sol.exists():
            missing.append((ex, sol))
    assert not missing, f'Missing solution files for exercises: {missing}'
