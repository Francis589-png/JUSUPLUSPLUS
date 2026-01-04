"""Execute all notebooks under course/notebooks and return non-zero on failure."""
import sys
from pathlib import Path
import nbformat
from nbclient import NotebookClient, CellExecutionError

ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK_DIR = ROOT / "course" / "notebooks"


def run_notebook(nb_path: Path, timeout=120):
    print('Executing', nb_path)
    nb = nbformat.read(nb_path, as_version=4)
    client = NotebookClient(nb, timeout=timeout, kernel_name='python3')
    try:
        client.execute()
        print('SUCCESS:', nb_path)
        return 0
    except CellExecutionError as e:
        print('FAILED:', nb_path, e)
        return 1


def main():
    if not NOTEBOOK_DIR.exists():
        print('No notebooks directory:', NOTEBOOK_DIR)
        return 0
    errors = 0
    for nb in sorted(NOTEBOOK_DIR.glob('*.ipynb')):
        errors += run_notebook(nb)
    if errors:
        print('Notebook execution completed with failures:', errors)
        return 2
    print('All notebooks executed successfully')
    return 0


if __name__ == '__main__':
    sys.exit(main())
