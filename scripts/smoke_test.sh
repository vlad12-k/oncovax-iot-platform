#!/usr/bin/env bash
set -e

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
