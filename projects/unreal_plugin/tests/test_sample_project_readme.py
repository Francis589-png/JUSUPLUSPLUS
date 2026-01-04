from pathlib import Path


def test_sample_project_readme_exists():
    p = Path('projects') / 'unreal_plugin' / 'unreal_sample_project' / 'README.md'
    assert p.exists()
    txt = p.read_text()
    assert 'Install into your project' in txt
    assert 'Blueprint quick recipe' in txt
