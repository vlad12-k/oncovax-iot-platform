# Changelog

All notable changes to this repository are documented in this file.

## [Unreleased]

### Added
- Final release metadata baseline via this changelog.

### Changed
- README and canonical docs alignment for runtime/hosted architecture references, proof-surface framing, and scope-boundary language.
- Demo/walkthrough/evidence documentation consistency across `README.md`, `docs/EVIDENCE_MAP.md`, `docs/DEMO_WALKTHROUGH.md`, and `docs/DEMO_SCENARIOS.md`.
- Operator documentation consistency across:
  - `docs/RUNBOOK.md`
  - `OPS_RUNBOOK.md`
  - `docs/RECOVERY_AND_ROLLBACK.md`
  - `docs/OBSERVABILITY.md`
  - `docs/THREAT_MODEL.md`
- Minor wording polish in:
  - `tests/integration/README.md`
  - `services/simulator/scenarios/README.md`

### Removed
- Stale placeholder/keep artifacts and superseded release-surface leftovers:
  - `demo/recording.gif`
  - `tools/postman_collection.json`
  - `.gitkeep` / `.keep` placeholder files no longer needed for tracked-empty directories

### Verification
- Canonical local verification path: `make verify-local` (pass on current branch state during final packaging).
