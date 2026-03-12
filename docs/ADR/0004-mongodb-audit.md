# ADR 0004: Use MongoDB (Atlas later) for audit trail and metadata
## Status
Proposed (Dev: local; Later: Atlas)
## Context
Audit trails (acknowledgements, config changes, incident notes) are document-like and need flexible structure.
## Decision
Use MongoDB for audit events and metadata; migrate to MongoDB Atlas for a production-like demo.
## Consequences
Pros: flexible event documents, easy to query timelines, Atlas managed option.
Cons: requires strict no-secrets handling and least-privilege access.
Mitigations: `.env` ignored, `.env.example` placeholders, RBAC in API, security scanning.
