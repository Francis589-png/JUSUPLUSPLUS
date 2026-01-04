# Sandbox Runner

Jusu++ provides a simple sandbox runner to execute programs in a subprocess
with a wall-clock timeout and (on Unix) an address-space memory limit.

APIs
- `runtime.sandbox.run_file(path, timeout=5.0, memory_limit_mb=None, backend='interp')`
- `runtime.sandbox.run_source(src, ...)` writes the source to a temp file and runs it.

Notes
- Memory limits use `resource.RLIMIT_AS` and are effective only on Unix-like systems.
- Timeouts are enforced by the parent process (subprocess.run with timeout) and will
  return `timed_out=True` when the child exceeded the wall-clock limit.

Example

```python
from runtime import sandbox

res = sandbox.run_source('''
function main():
    i = 0
    while true:
        i = i + 1
    end
end

''', timeout=1.0)
print(res)
```
