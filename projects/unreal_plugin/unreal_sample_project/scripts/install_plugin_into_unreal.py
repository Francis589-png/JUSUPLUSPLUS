"""Copy and unpack the example plugin into an Unreal project Plugins/ folder.

Usage:
  python install_plugin_into_unreal.py /path/to/YourUnrealProject

The script expects the packaged `unreal_example_plugin.zip` created by the packaging helper.
"""
import shutil
from pathlib import Path
import argparse
import zipfile

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / 'artifacts' / 'unreal_example_plugin.zip'


def install(target_project: Path):
    if not target_project.exists():
        raise SystemExit(f'Target project not found: {target_project}')
    plugins_dir = target_project / 'Plugins'
    plugins_dir.mkdir(parents=True, exist_ok=True)
    if not ARTIFACT.exists():
        raise SystemExit('Plugin artifact not found. Run tools/package_unreal_plugin.py first.')
    with zipfile.ZipFile(ARTIFACT, 'r') as z:
        z.extractall(str(plugins_dir))
    print('Plugin installed into', plugins_dir)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('target', help='Path to an Unreal project root')
    args = p.parse_args()
    install(Path(args.target))
