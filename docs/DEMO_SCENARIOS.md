# Demo Scenarios

These scenarios are designed for recruiter/demo walkthroughs while preserving production-safe defaults.

For a single start-to-finish run order, use [DEMO_WALKTHROUGH.md](DEMO_WALKTHROUGH.md).

## Scenario 1: Healthy steady-state telemetry

- Show continuous telemetry arrival.
- Confirm dashboard/API summary reflects normal operation.
- Confirm no critical alerts are active.

## Scenario 2: Temperature excursion

- Inject or simulate out-of-range temperature readings.
- Observe alert creation and visibility in API/dashboard.
- Demonstrate acknowledgement workflow.

## Scenario 3: Low battery trend

- Show battery degradation telemetry pattern.
- Demonstrate corresponding alert/event visibility.

## Scenario 4: Offline device behavior

- Pause telemetry for a device profile.
- Demonstrate offline detection expectations and operator runbook action.

## Scenario 5: Door-open / handling breach

- Simulate prolonged door-open condition.
- Demonstrate event logging and escalation expectations.

## Demo evidence checklist

- Screenshot of API summary endpoint output.
- Screenshot of dashboard with active data window.
- Screenshot of Grafana panel after import (when dashboard exports are added).
- Example acknowledged alert payload/response.

## Reviewer notes

- Keep focus on demonstrated behavior and evidence already present in repo.
- Do not claim production guarantees beyond documented deployment/runbook boundaries.
- Treat Node-RED demo-control as optional/dev-only orchestration support, not canonical ingestion.
