"""Validate all Compose files without reading or creating a real deployment .env."""
from pathlib import Path
import subprocess
import tempfile
import yaml

root = Path(__file__).resolve().parents[1]
for path in sorted((root / 'infra').glob('docker-compose*.yml')):
    model = yaml.safe_load(path.read_text())
    for service in model['services'].values():
        if 'env_file' in service:
            service['env_file'] = [str(root / 'infra/.env.example')]
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml') as temporary:
        yaml.safe_dump(model, temporary)
        temporary.flush()
        subprocess.run(['docker', 'compose', '--project-directory', str(root / 'infra'),
                        '-f', temporary.name, 'config', '--quiet'], check=True)
    print(f'Validated {path.name}')
