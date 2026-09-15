# Release Validation Checklist

Record the commit, environment, command results and skipped checks in the release review. Unchecked items are not evidence of success.

## Source and contracts

- [ ] Install `requirements-dev.txt` in a clean Python environment.
- [ ] Run `make verify-static`: pytest, Python/shell syntax and all Compose configurations.
- [ ] Confirm local documentation links, referenced assets and archived screenshot checksums pass.
- [ ] Review the staged diff, tracked files and secrets scan; retain authorship and license terms.

## Local runtime

- [ ] Run `make verify-local` with Docker running and required loopback ports free.
- [ ] Confirm a uniquely identified telemetry probe reaches InfluxDB, generates an alert in MongoDB/API, and can be acknowledged.
- [ ] Confirm Grafana has its datasource/dashboard and populated telemetry panels.
- [ ] Exercise scenario selection, temporary runtime events and reset; inspect status messages and metric changes.
- [ ] Verify restart/reconnect behavior using the [runbook](RUNBOOK.md).

## Deployment lifecycle

- [ ] README, evidence map, walkthrough and deployment guide identify DigitalOcean as decommissioned.
- [ ] Historical screenshots and recordings are labeled as archived observations.
- [ ] Distinguish owner-reported shutdown from pre-destruction screenshots; do not infer a deletion timestamp or zero bill.
- [ ] If redeploying: validate DNS, TLS, unauthenticated rejection and authenticated API/Grafana paths on a host you control.
- [ ] Record hosted checks as not applicable while hosting is decommissioned.

## Release gate

- [ ] CI passes on the release branch and the PR is reviewed.
- [ ] Runtime checks pass, or the release review clearly records the outstanding environment blocker.
- [ ] Validate recovery with actual backups before making recovery guarantees.
- [ ] Publish v0.2.0 only from the reviewed, merged commit.
- [ ] Delete old branches only after checking ancestry or confirming their changes were superseded.

The release remains a software-simulated engineering baseline, without clinical certification, regulatory validation, immutable audit logging, or complete application-level authorization.
