from pathlib import Path
import subprocess


def test_render_notebooks():
    # Skip if nbformat isn't installed
    try:
        import nbformat  # type: ignore
    except Exception:
        import pytest
        pytest.skip('nbformat not installed')

    script = Path('course') / 'tools' / 'render_notebooks.py'
    assert script.exists()
    r = subprocess.run(['python', str(script)], capture_output=True, text=True)
    print(r.stdout)
    assert r.returncode == 0
    # Verify at least one HTML file written
    out_dir = Path('docs') / 'course' / 'notebooks_html'
    assert out_dir.exists()
    assert any(out_dir.glob('*.html'))
