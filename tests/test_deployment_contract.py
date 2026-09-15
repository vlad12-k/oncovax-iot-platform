from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def compose(name):
    return yaml.safe_load((ROOT / 'infra' / name).read_text())['services']


def test_hosted_services_are_not_directly_published():
    services = compose('docker-compose.prod.yml')
    assert 'worker' in services
    for name, service in services.items():
        if name != 'nginx':
            assert not service.get('ports'), name
    assert './nginx/.htpasswd:/etc/nginx/conf.d/.htpasswd:ro' in services['nginx']['volumes']


def test_local_services_bind_loopback():
    for service in compose('docker-compose.dev.yml').values():
        assert all(port.startswith('127.0.0.1:') for port in service.get('ports', []))


def test_ingress_has_tls_and_protected_operator_routes():
    config = (ROOT / 'infra/nginx/nginx.conf').read_text()
    assert 'ssl_certificate ' in config
    assert 'ssl_certificate_key ' in config
    assert 'auth_basic_user_file /etc/nginx/conf.d/.htpasswd;' in config
    assert 'location = /public-health' in config
