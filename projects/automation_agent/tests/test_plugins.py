from projects.automation_agent.plugins import echo_plugin


def test_echo_plugin_contract():
    assert hasattr(echo_plugin, 'name')
    assert echo_plugin.name == 'echo'
    res = echo_plugin.run({'a': 1})
    assert res['message'] == 'echo'
    assert res['context']['a'] == 1
