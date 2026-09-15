import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_smoke_propagates_http_failure(tmp_path):
    # A reachable server returning HTTP 500 must fail validation, not print success.
    curl = tmp_path / 'curl'
    curl.write_text('#!/bin/sh\ncase "$*" in *--fail*) exit 22;; *) exit 0;; esac\n')
    curl.chmod(0o755)
    result = subprocess.run(['bash', 'scripts/smoke_test.sh', '--prod', 'example.invalid', 'operator', 'test'],
        cwd=ROOT, env={**os.environ, 'PATH': str(tmp_path) + ':' + os.environ['PATH']}, capture_output=True)
    assert result.returncode == 22


def test_verify_local_runs_static_checks_before_startup():
    result = subprocess.run(['make', '-n', 'verify-local'], cwd=ROOT, text=True, capture_output=True, check=True)
    commands = result.stdout
    assert commands.index('-m pytest') < commands.index('up -d --build') < commands.index('./scripts/smoke_test.sh')
    assert '--wait' in commands
    assert 'scripts/verify_pipeline.py' in commands
