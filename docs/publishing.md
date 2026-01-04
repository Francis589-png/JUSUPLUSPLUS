# Publishing Jusu++ and Plugins

Publishing core package
- Use `python -m build` to build wheels/sdist and `twine upload` to publish.
- Use Git tags `vX.Y.Z` to trigger TestPyPI publish workflow; set `TESTPYPI_TOKEN` in repository secrets.

Extras and optional dependencies
- Install data tools: `pip install jusu-language[datatools]`
- Install wasm support: `pip install jusu-language[wasm]`

Plugin packaging
- Use `tools/init_jusu_package.py <name>` to scaffold a plugin and add the
  `[project.entry-points]` as shown in `docs/packages.md`.

Publishing a plugin
- Publish the plugin to PyPI or TestPyPI as usual; users will be able to
  install and `arpah.discover_plugins()` will find it if it exposes the
  `jusu.plugins` entry point group.
