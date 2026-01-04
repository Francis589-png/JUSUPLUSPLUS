from projects.automation_agent.agent import Agent
from pathlib import Path


def test_discovery_and_run(tmp_path):
    # copy the sample plugins to a temp dir and point Agent at it
    sample_dir = Path('projects') / 'automation_agent' / 'plugins'
    dest = tmp_path / 'plugins'
    dest.mkdir()
    for p in sample_dir.glob('*.py'):
        if p.is_file():
            (dest / p.name).write_text(p.read_text())
    a = Agent(plugins_dir=dest)
    a.discover()
    assert 'echo' in a.plugins
    res = a.run_plugin('echo', {'k': 1})
    assert res['message'] == 'echo'


def test_run_all_returns_dict():
    a = Agent()
    a.discover()
    r = a.run_all({'hello': 'world'})
    assert isinstance(r, dict)
    # echo plugin should be present in typical repo
    if 'echo' in r:
        assert 'message' in r['echo']
