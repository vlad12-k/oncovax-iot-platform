#!/usr/bin/env bash
# Validate the retained ingress config with disposable certificates and local DNS stubs.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CERT_DIR="$(mktemp -d)"
trap 'rm -rf "$CERT_DIR"' EXIT
for domain in oncovax.live grafana.oncovax.live; do
  mkdir -p "$CERT_DIR/live/$domain"
  openssl req -x509 -newkey rsa:2048 -nodes -days 1 -subj "/CN=$domain" \
    -keyout "$CERT_DIR/live/$domain/privkey.pem" \
    -out "$CERT_DIR/live/$domain/fullchain.pem" >/dev/null 2>&1
done
docker run --rm --add-host api:127.0.0.1 --add-host grafana:127.0.0.1 \
  -v "$ROOT_DIR/infra/nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro" \
  -v "$CERT_DIR:/etc/letsencrypt:ro" nginx:1.27-alpine nginx -t
