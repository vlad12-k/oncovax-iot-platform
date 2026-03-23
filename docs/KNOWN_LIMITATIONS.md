# Known Limitations

The following limitations are known in the current baseline and are tracked for incremental improvement.

- Simulator realism and scenario orchestration are still evolving.
- Node-RED and Grafana exports are scaffolded and may be placeholders until finalized.
- Alert taxonomy is broader in target architecture than current runtime implementation.
- Current UI is lightweight and focused on operational baseline behavior.
- Full production hardening requires environment-specific controls beyond repository defaults.

## Security and operations

- No live secrets are stored in repository artifacts.
- Production ingress/auth behavior is intentionally preserved during documentation-only phases.

## Upgrade strategy

Limitations should be addressed through additive phases with regression checks, avoiding destructive rewrites.
