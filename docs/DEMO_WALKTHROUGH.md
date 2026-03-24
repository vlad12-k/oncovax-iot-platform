# Demo Walkthrough – Recruiter/Instructor Flow

## Purpose

This walkthrough provides a single, reproducible path to demonstrate OncoVax end-to-end with evidence checkpoints.
It is intentionally presentation-oriented and does not change runtime architecture.

---

## 0) What to show in one sentence

OncoVax monitors cold-storage telemetry through an MQTT → worker pipeline, stores and visualizes telemetry/alerts, and supports operational alert workflows with auditability and hosted/live verification paths.

---

## 1) Open the repository and orient quickly (2 minutes)

1. Read `README.md` section **Recruiter / instructor quick review (10–15 minutes)**.
2. Confirm capability baseline in `docs/OVERVIEW.md`.
3. Keep `docs/EVIDENCE_MAP.md` open for claim-to-proof cross-reference.

Expected outcome:

- Reviewer understands what the platform is, why it matters, and what proof surfaces exist.

---

## 2) Start local stack and verify health (2–3 minutes)

Run:

```bash
docker compose -f infra/docker-compose.dev.yml up -d --build
./scripts/smoke_test.sh
```

Expected outcome:

- Services start successfully.
- Smoke checks return healthy responses.

Evidence anchors:

- `docs/RUNBOOK.md` (service + smoke commands)
- `demo/screenshots/sprint_8_fig_smoke_test_with_api_check_terminal.png`

---

## 3) Show core operational API proof (2 minutes)

Run:

```bash
curl -s http://localhost:8000/summary | python -m json.tool
curl -s "http://localhost:8000/alerts?limit=20" | python -m json.tool
```

Expected outcome:

- Summary counts are returned.
- Alert records are visible for operator workflow context.

Evidence anchors:

- `demo/screenshots/sprint_10_fig_api_summary_terminal.png`
- `demo/screenshots/sprint_10_fig_api_filtered_unacknowledged_alerts_terminal.png`

---

## 4) Show dashboard + acknowledgement workflow (2 minutes)

1. Open `http://localhost:8000`.
2. Demonstrate:
   - summary cards,
   - alert filtering/search,
   - alert acknowledgement flow.

Expected outcome:

- Reviewer sees usable operator workflow and acknowledgement UX.

Evidence anchors:

- `demo/screenshots/sprint_11_fig_operational_dashboard_main_view.png`
- `demo/screenshots/sprint_11_fig_operational_dashboard_filtered_view.png`
- `demo/screenshots/sprint_11_fig_operational_dashboard_search_view.png`

---

## 5) Show observability proof in Grafana (2–3 minutes)

1. Follow `grafana/README.md` import steps.
2. Import `grafana/dashboards/oncovax-observability-final.v1.json`.
3. Set time range to include active simulator traffic.

Expected outcome:

- Telemetry ingest and alert panels move with live data.
- Per-device trends and recent alert table are visible.

Evidence anchors:

- `grafana/README.md`
- `grafana/dashboards/oncovax-observability-final.v1.json`

---

## 6) Show control-plane behavior proof (D2) (optional but strong)

Use D2 commands from `docs/RUNBOOK.md`:

- `scenario/select`
- `mode/set`
- `event/trigger` (`burst_pulse`, `breach_pulse`, `offline_pulse`)
- `reset_runtime`

Expected outcome:

- Behavior changes are observable in telemetry/alert trends as documented in `grafana/README.md`.

Evidence anchors:

- `docs/RUNBOOK.md` (D2 runtime control section)
- `grafana/README.md` (runtime-control visibility expectations)

---

## 7) Show cloud/live proof path (Prompt E)

Run production-like smoke test (when live credentials are available):

```bash
./scripts/smoke_test.sh --prod oncovax.live oncovax-operator '<password>'
```

Expected outcome:

- Public health endpoint works unauthenticated.
- Protected summary endpoint works with credentials.

Evidence anchors:

- `docs/RUNBOOK.md` production-like smoke section
- `demo/screenshots/sprint_12_fig_digitalocean_hosted_api_terminal.png`
- `demo/screenshots/sprint_12_fig_digitalocean_hosted_dashboard_view.png`

---

## 8) Close with evidence map and limitations (1 minute)

1. Walk through `docs/EVIDENCE_MAP.md` proof surfaces.
2. Highlight boundary realism from `docs/KNOWN_LIMITATIONS.md`.

Expected outcome:

- Reviewer sees explicit evidence traceability and honest scope boundaries.

---

## Fast fallback path (if time is only 5 minutes)

1. `README.md` quick review section.
2. `./scripts/smoke_test.sh`.
3. `curl -s http://localhost:8000/summary | python -m json.tool`.
4. Open `http://localhost:8000`.
5. Show `docs/EVIDENCE_MAP.md` + `demo/screenshots/README.md`.
