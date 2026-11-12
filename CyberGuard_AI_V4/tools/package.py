"""Build a distributable ZIP without local state or cached bytecode."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parents[1]
output = root.parent / 'CyberGuard_AI_V4.zip'
with ZipFile(output, 'w', compression=ZIP_DEFLATED) as archive:
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root)
        if any(p in {'.venv', '.git', '__pycache__', 'runtime', '.pytest_cache'} or p.startswith('tmp') for p in relative.parts):
            continue
        if path.is_file() and path.suffix not in ('.pyc', '.log'):
            archive.write(path, root.name + '/' + relative.as_posix())
print(output)
