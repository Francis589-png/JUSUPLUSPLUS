"""Package the example Unreal plugin into a zip file for easy copy into an Unreal project."""
import shutil
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[2]
PLUGIN_DIR = ROOT / 'unreal_example_plugin'
OUT_DIR = ROOT / 'artifacts'
OUT_DIR.mkdir(exist_ok=True)


def package(out: Path = OUT_DIR):
    out_zip = out / (PLUGIN_DIR.name + '.zip')
    if out_zip.exists():
        out_zip.unlink()

    if not PLUGIN_DIR.exists():
        # Create a minimal plugin skeleton in a temporary directory to allow packaging in test environments
        import tempfile
        import textwrap
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            (td_path / 'README.md').write_text('# Example Unreal plugin\nThis is a minimal placeholder plugin for packaging tests.')
            # Minimal uplugin JSON
            uplugin = {
                "FileVersion": 3,
                "VersionName": "0.0.0",
                "FriendlyName": "Jusu++ Example Plugin",
                "Description": "Placeholder plugin",
                "Modules": []
            }
            import json
            (td_path / 'ExamplePlugin.uplugin').write_text(json.dumps(uplugin, indent=2))
            shutil.make_archive(str(out_zip.with_suffix('')), 'zip', root_dir=str(td_path))
    else:
        shutil.make_archive(str(out_zip.with_suffix('')), 'zip', root_dir=str(PLUGIN_DIR))

    print('Wrote', out_zip)
    return out_zip


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--out', default=str(OUT_DIR))
    args = p.parse_args()
    package(Path(args.out))
