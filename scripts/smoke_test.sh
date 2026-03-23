#!/usr/bin/env bash
set -e

if [[ "${1:-}" == "--prod" ]]; then
  DOMAIN="${2:-}"
  USERNAME="${3:-}"
  PASSWORD="${4:-}"

  if [[ -z "$DOMAIN" || -z "$USERNAME" || -z "$PASSWORD" ]]; then
    echo "usage: $0 --prod <domain> <username> <password>" >&2
    exit 1
  fi

  echo "[smoke] checking public health through nginx"
  curl -s "https://$DOMAIN/public-health"

  echo
  echo "[smoke] checking authenticated summary through nginx"
  curl -s -u "$USERNAME:$PASSWORD" "https://$DOMAIN/summary"

  echo
  echo "[smoke] done (prod)"
  exit 0
fi

echo "[smoke] checking docker containers"
docker ps --format "table {{.Names}}\t{{.Status}}" | sed -n '1,10p'

echo
echo "[smoke] checking InfluxDB health"
curl -s http://localhost:8086/health

echo
echo "[smoke] checking Grafana login page"
curl -I -s http://localhost:3000/login | head -n 1

echo
echo "[smoke] checking API health"
curl -s http://localhost:8000/health

echo
echo "[smoke] checking MongoDB container"
docker exec mongodb mongosh --quiet --eval 'db.runCommand({ ping: 1 })'

echo
echo "[smoke] done"
