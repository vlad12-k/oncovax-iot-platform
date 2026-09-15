# Deployment Archive

The DigitalOcean hosted deployment was previously operationally validated and later intentionally decommissioned for cost control after the available cloud credits were exhausted. No active hosted OncoVax service is advertised by this release.

## Retained evidence

- [Shutdown evidence checksums](deployment-evidence/2026-08-09-digitalocean-shutdown/SHA256SUMS.txt) cover the archived screenshots.
- [Runtime screenshots](../demo/screenshots/README.md) show earlier API, dashboard, Atlas and hosting sessions.
- [Archived Grafana captures](../docs/assets/archived-hosted/archived-hosted-grafana-temperature-by-device.png) show historical time-series behavior.
- Compose, nginx, [runbooks](RUNBOOK.md), and [recovery guidance](RECOVERY_AND_ROLLBACK.md) describe the retained deployment configuration.

The archive directory is named `2026-08-09-digitalocean-shutdown`; its screenshot filenames are dated 2026-08-10. Those dates identify the archive/capture sessions, not a verified exact destruction timestamp. The retained images include pre-destruction resource inventories and an access timeout. The lifecycle status above records the owner's shutdown account; the screenshots alone do not prove resource deletion or a zero ongoing bill.

Historical hostname `oncovax.live`, IP addresses, Grafana URLs, and uptime signals are evidence context. Before redeployment, choose and configure a hostname you control, provision new credentials and certificates, review the security boundaries, and rerun validation.

Credentials, TLS private keys and database backups are not bundled. Screenshots and configuration cannot restore database contents. See [recovery prerequisites](RECOVERY_AND_ROLLBACK.md).
