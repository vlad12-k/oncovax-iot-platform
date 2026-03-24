from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
README_PATH = REPO_ROOT / "README.md"
EVIDENCE_MAP_PATH = REPO_ROOT / "docs" / "EVIDENCE_MAP.md"
DEMO_SCENARIOS_PATH = REPO_ROOT / "docs" / "DEMO_SCENARIOS.md"
DEMO_WALKTHROUGH_PATH = REPO_ROOT / "docs" / "DEMO_WALKTHROUGH.md"
SCREENSHOTS_INDEX_PATH = REPO_ROOT / "demo" / "screenshots" / "README.md"


def test_prompt_g_demo_docs_exist():
    assert README_PATH.exists()
    assert EVIDENCE_MAP_PATH.exists()
    assert DEMO_SCENARIOS_PATH.exists()
    assert DEMO_WALKTHROUGH_PATH.exists()
    assert SCREENSHOTS_INDEX_PATH.exists()


def test_prompt_g_readme_links_review_and_demo_entrypoints():
    text = README_PATH.read_text(encoding="utf-8")
    assert "Recruiter / instructor quick review (10–15 minutes)" in text
    assert "docs/DEMO_WALKTHROUGH.md" in text
    assert "docs/EVIDENCE_MAP.md" in text
    assert "demo/screenshots/README.md" in text


def test_prompt_g_evidence_map_contains_reviewer_first_surfaces():
    text = EVIDENCE_MAP_PATH.read_text(encoding="utf-8")
    assert "Reviewer-first proof surfaces (Prompt G)" in text
    assert "C) Observability proof" in text
    assert "D) Control-plane proof (D2)" in text
    assert "E) Cloud/live proof (Prompt E)" in text
    assert "Prompt G demo-review sequence" in text


def test_prompt_g_demo_walkthrough_covers_end_to_end_flow():
    text = DEMO_WALKTHROUGH_PATH.read_text(encoding="utf-8")
    assert "Demo Walkthrough – Recruiter/Instructor Flow" in text
    assert "docker compose -f infra/docker-compose.dev.yml up -d --build" in text
    assert "./scripts/smoke_test.sh" in text
    assert "grafana/dashboards/oncovax-observability-final.v1.json" in text
    assert "./scripts/smoke_test.sh --prod oncovax.live oncovax-operator '<password>'" in text


def test_prompt_g_demo_scenarios_reference_walkthrough_and_reviewer_notes():
    text = DEMO_SCENARIOS_PATH.read_text(encoding="utf-8")
    assert "DEMO_WALKTHROUGH.md" in text
    assert "## Reviewer notes" in text
    assert "Node-RED demo-control as optional/dev-only" in text


def test_prompt_g_screenshots_index_groups_visual_evidence():
    text = SCREENSHOTS_INDEX_PATH.read_text(encoding="utf-8")
    assert "# Demo Screenshots Evidence Index" in text
    assert "## 1) API and workflow proof" in text
    assert "## 2) Dashboard usability proof" in text
    assert "## 3) Deployment/readiness proof" in text
    assert "## 4) Cloud/live proof" in text
