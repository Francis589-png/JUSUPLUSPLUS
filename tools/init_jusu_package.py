"""Scaffold a minimal Jusu++ package with an entry point for `jusu.plugins`.

Usage: python tools/init_jusu_package.py <package-name>
This creates a directory with a simple pyproject.toml and a plugin module.
"""
import os
import sys

TEMPLATE_PYPROJECT = """[project]
name = "{pkg}"
version = "0.0.0"
requires-python = ">=3.10"
description = "Jusu++ plugin package: {pkg}"

[project.entry-points]
"jusu.plugins" = [
    "{pkg} = {pkg}.plugin:load"
]
"""

TEMPLATE_PLUGIN = """def load():
    \"\"\"Factory returning a module-like object for Jusu builtins.\"\"\"
    class Mod:
        def hello(self):
            return 'hello from {pkg}'
    return Mod()
"""


def main(name: str):
    if os.path.exists(name):
        print('Directory exists; aborting')
        return
    os.makedirs(name)
    with open(os.path.join(name, 'pyproject.toml'), 'w') as f:
        f.write(TEMPLATE_PYPROJECT.format(pkg=name))
    os.makedirs(os.path.join(name, name))
    with open(os.path.join(name, name, 'plugin.py'), 'w') as f:
        f.write(TEMPLATE_PLUGIN.format(pkg=name))
    print(f'Created package {name}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python tools/init_jusu_package.py <package-name>')
    else:
        main(sys.argv[1])