"""Scaffold helper for an Unreal integration plugin (prototype)
Creates a directory structure with a sample README and integration notes for adding a minimal C++/Blueprint side plugin that talks to the bridge.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'unreal_example_plugin'

TEMPLATE = {
    'Plugin.uplugin': '{"FileVersion": 3, "Version": 1, "VersionName": "0.1", "FriendlyName": "JusuUnrealPlugin", "Description": "Example plugin showing how to call an external Jusu++ bridge.", "Category": "Scripting"}',
    'README.md': '# Example Unreal plugin\nThis folder contains notes and a minimal example to integrate with `jusu_unreal_bridge.py`.\nAdd a C++ module that connects to the bridge over TCP or uses the HTTP bridge approach.'
}


def scaffold(out_dir: Path = OUT):
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, content in TEMPLATE.items():
        p = out_dir / name
        p.write_text(content)
    print('Scaffolded plugin at', out_dir)


if __name__ == '__main__':
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT
    scaffold(target)
