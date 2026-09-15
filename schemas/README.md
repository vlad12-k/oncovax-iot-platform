# Baseline data contracts

- `telemetry.schema.json`: canonical records after simulator normalization; validated by the worker at ingestion.
- `alert.schema.json`: the worker's temperature excursion object before storage (`ts`, threshold, value, active status and breach count).
- `audit_event.schema.json`: the persisted alert lifecycle/API record (`time`, alert ID and acknowledgement fields). Acknowledged records require an operator and acknowledgement timestamp.

Alert and audit contracts are checked against actual worker/API output by tests; they are not additional runtime validators. Audit records permit database extension fields and are mutable. The API removes MongoDB `_id` from responses.

Unused device-metadata and multi-device profile scaffolding was removed because no runtime consumes it. Runtime device profiles remain in the simulator implementation. JSON Schema format checks are explicitly enabled in contract tests; the existing ingestion validator does not enforce timestamp format.
