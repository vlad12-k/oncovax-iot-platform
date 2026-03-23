# Recovery and Rollback

This document defines safe rollback and recovery actions for the current deployment model.

## Principles

- Prefer rollback over risky live hotfixes.
- Preserve ingress/auth configuration and monitoring route behavior.
- Validate system health after each action.

## Recovery steps (service-level)

1. Inspect service status and logs.
2. Restart only affected service.
3. Verify dependencies (MQTT, InfluxDB, MongoDB/Atlas, API).
4. Verify `/health` and `/public-health` checks.

## Rollback steps (application changes)

1. Identify last known good commit/image.
2. Redeploy previous version via existing compose workflow.
3. Verify API health and alert listing behavior.
4. Verify ingress protection and public-health endpoint behavior.

## Data recovery notes

- Restore MongoDB/Atlas data per managed backup process.
- Restore InfluxDB data from retention/backups as configured.
- Record recovery timeline and incident notes in audit process.

## Post-recovery checklist

- API health check returns success.
- Public health endpoint reachable without auth.
- Protected routes remain auth-gated.
- Alert acknowledgement flow still functions.
