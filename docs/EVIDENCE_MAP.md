# Evidence Map

Evidence is scoped to source behavior, repeatable local checks, or historical hosting observations. A passing static check does not establish runtime availability.

| Claim | Source / verification | Boundary |
| --- | --- | --- |
| Canonical telemetry validation and excursion evaluation | [worker](../services/worker/worker.py), [contract tests](../tests/test_data_contracts.py) | Simulated inputs; no physical-device certification |
| Alert persistence and acknowledgement | `make verify-local`, [API routes](../services/api/routes/alerts.py) | Mutable MongoDB records; no immutable audit-log guarantee |
| Simulator runtime controls | [controller tests](../tests/test_simulator_runtime_control.py), [adapter tests](../tests/test_orchestration_adapter.py) | MQTT control plane is intended for controlled environments |
| Dashboard queries and datasource wiring | [observability tests](../tests/test_observability_artifacts.py), [Grafana guide](../grafana/README.md) | Query presence alone does not prove populated panels |
| TLS ingress separation | [deployment tests](../tests/test_deployment_contract.py), [nginx configuration](../infra/nginx/nginx.conf) | Certificates, secrets, DNS and a running host are required |
| Archived hosting observations | [deployment archive](DEPLOYMENT_ARCHIVE.md), [screenshot catalog](../demo/screenshots/README.md) | Historical only; hosting was decommissioned |
| Archive file integrity | [evidence tests](../tests/test_evidence_integrity.py) | Checksums detect file changes, not truth of pictured claims |
| Repeatable release verification | [Makefile](../Makefile), [CI](../.github/workflows/ci.yml), [checklist](FINAL_VALIDATION_CHECKLIST.md) | Record skipped checks explicitly |

## Reproduction

1. Install the development requirements and run `make verify-static`.
2. Start Docker and run `make verify-local` for a fresh end-to-end probe.
3. Follow the [walkthrough](DEMO_WALKTHROUGH.md) to inspect Grafana and runtime control reactions.
4. Validate ingress only on a newly provisioned host under your control.

External uptime monitoring establishes endpoint reachability for the recorded period. It does not establish processing correctness, data integrity, access control, or ongoing uptime after shutdown.
