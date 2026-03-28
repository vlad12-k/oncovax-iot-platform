# OncoVax Ops Runbook

## Health checks
```bash
curl -iS https://oncovax.live/public-health
docker exec oncovax-api python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8000/health").read().decode())'
docker exec oncovax-api python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8000/summary").read().decode())'
docker exec oncovax-api python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8000/alerts?limit=3").read().decode())'
```

## Restart stack
```bash
cd /opt/oncovax/infra
docker compose -f docker-compose.prod.yml restart
docker compose -f docker-compose.prod.yml ps
```

## Force recreate
```bash
cd /opt/oncovax/infra
docker compose -f docker-compose.prod.yml up -d --force-recreate
docker compose -f docker-compose.prod.yml ps
```

## Logs
```bash
docker logs --since=10m oncovax-api
docker logs --since=10m oncovax-worker
docker logs --since=10m oncovax-nginx
docker logs --since=10m oncovax-simulator
```

## Monitoring proof
- public endpoint must return HTTP 200 and {"status":"ok"}
- nginx logs should show public-health checks
- API must return summary and alerts internally

## Rollback snapshot
Use latest folder in /opt/oncovax/backups/

Restore at minimum:
- infra/docker-compose.prod.yml
- infra/nginx/nginx.conf

Then run:
```bash
cd /opt/oncovax/infra
docker compose -f docker-compose.prod.yml up -d --force-recreate
```
