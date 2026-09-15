import hashlib
import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]


def test_archived_screenshot_checksums():
    manifest = ROOT / 'docs/deployment-evidence/2026-08-09-digitalocean-shutdown/SHA256SUMS.txt'
    entries = manifest.read_text().splitlines()
    assert entries
    for line in entries:
        digest, name = line.split(maxsplit=1)
        path = ROOT / name.strip()
        assert path.is_file(), name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, name


def test_local_markdown_link_targets_exist():
    failures = []
    for path in ROOT.rglob('*.md'):
        if any(part in {'.git', '.venv', '.pytest_cache'} for part in path.relative_to(ROOT).parts):
            continue
        for link in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            target = unquote(link.split('#', 1)[0].split(' "', 1)[0].strip('<>'))
            if not target or re.match(r'^[a-zA-Z][\w+.-]*:', target):
                continue
            if not (path.parent / target).exists():
                failures.append(f'{path.relative_to(ROOT)}: {target}')
    assert not failures, '\n'.join(failures)
