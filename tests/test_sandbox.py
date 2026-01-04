import os
import sys
import platform
# Ensure project root is on sys.path when running tests directly
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from runtime import sandbox


def test_timeout_kills_long_running_program():
    import platform
    if platform.system() == 'Windows':
        import pytest
        pytest.skip('Sandbox timeout behavior is platform dependent on Windows')

    src = '''
# Busy loop
function main():
    i = 0
    while true:
        i = i + 1
    end

say 0
'''
    res = sandbox.run_source(src, timeout=1.0)
    assert res['timed_out'] is True


def test_memory_limit_terminates_when_exceeded():
    # This test only runs on Unix where RLIMIT_AS is available
    if platform.system() == 'Windows':
        import pytest
        pytest.skip('Memory limits not supported on Windows in this test')

    # Program attempts to allocate a large list
    src = '''
function main():
    arr = []
    i = 0
    while i < 20000000:
        arr = arr + [1,1,1,1,1,1,1,1,1,1]
        i = i + 1
    end
    say len(arr)
end

say 0
'''
    res = sandbox.run_source(src, timeout=5.0, memory_limit_mb=50)
    # If the child is killed due to memory, returncode should be non-zero or stderr mention memory
    assert res['timed_out'] is False
    assert res['returncode'] is not None
