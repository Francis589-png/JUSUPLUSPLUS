"""Render notebooks under course/notebooks to HTML using nbconvert."""
import sys
from pathlib import Path
import nbformat
from nbconvert import HTMLExporter

ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK_DIR = ROOT / 'course' / 'notebooks'
OUT_DIR = ROOT / 'docs' / 'course' / 'notebooks_html'
OUT_DIR.mkdir(parents=True, exist_ok=True)

exporter = HTMLExporter()
exporter.template_name = 'classic'

for nb in sorted(NOTEBOOK_DIR.glob('*.ipynb')):
    nb_node = nbformat.read(nb, as_version=4)
    body, _ = exporter.from_notebook_node(nb_node)
    out_path = OUT_DIR / (nb.stem + '.html')
    out_path.write_text(body, encoding='utf-8')
    print('Wrote', out_path)

print('Rendered', len(list(NOTEBOOK_DIR.glob('*.ipynb'))), 'notebooks')
