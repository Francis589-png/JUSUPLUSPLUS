# Packaging & Plugins for Jusu++

Overview
- Jusu++ supports third-party plugins that can be injected into the language builtins.
- Recommended distribution: standard Python package on PyPI exposing an
  entry point in the `jusu.plugins` group.

Entry point format (pyproject.toml):

[project.entry-points]
"jusu.plugins" = [
    "mytools = mytools.plugin:load"
]

Loader contract
- The referenced `load` (or factory) should be a callable that takes no
  arguments and returns a module-like object (e.g., an instance with
  methods/attributes) to be inserted into the Jusu builtins under the
  provided entry-point name.

Scaffolding
- Use `tools/init_jusu_package.py <package-name>` to create a minimal
  package with an example plugin module.

Runtime discovery
- At runtime, Jusu++ calls `runtime.pkgmgr.discover_plugins()` (also available via `runtime.arpah.discover_plugins()`) and
  injects discovered plugins into builtins (accessible as regular
  modules, e.g. `mytools.somefunc()` in Jusu code).

Arpah
- The package manager is exposed as `arpah` in `runtime.arpah` for clarity
  (alias to `pkgmgr` implementation). Use `arpah.register_builtin` or
  `arpah.discover_plugins()` when writing tooling or plugins.

JavaScript bridge (Node)

- The runtime exposes a `js` helper via `runtime.js` which allows calling Node.js modules or scripts:

```python
from runtime.js import call
res = call('my_module.js', 'add', [1,2])
```

- The bridge requires `node` available on PATH; tests are skipped when Node is missing.
- For stronger sandboxes, run Node calls inside the sandbox subprocess or compile code to WASM.
Publishing tips
- Put tests in the package and use `python -m build` to create wheels.
- Consider using the `[jusu]` extra to group optional deps for plugin
  development (convention only).