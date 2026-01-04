from pathlib import Path
from course.tools.grade_submission import grade_submission


def test_grade_example():
    sub = Path('course') / 'submissions' / 'example_lesson_01' / 'student_alice'
    assert sub.exists()
    r = grade_submission(sub)
    assert r['passed'] is True
    assert 'Hello, Alice' in r['output']
