from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
README_PATH = REPO_ROOT / "README.md"
CHECKLIST_PATH = REPO_ROOT / "docs" / "FINAL_VALIDATION_CHECKLIST.md"
EVIDENCE_MAP_PATH = REPO_ROOT / "docs" / "EVIDENCE_MAP.md"
MAKEFILE_PATH = REPO_ROOT / "Makefile"


def test_prompt_h_artifacts_exist():
    assert README_PATH.exists()
    assert CHECKLIST_PATH.exists()
    assert EVIDENCE_MAP_PATH.exists()
    assert MAKEFILE_PATH.exists()


def test_prompt_h_readme_is_single_primary_entrypoint_with_canonical_local_route():
    text = README_PATH.read_text(encoding="utf-8")
    assert "single primary entrypoint" in text
    assert "Zero-to-live-proof local route (Prompt H canonical path)" in text
    assert "make verify-local" in text
    assert "docs/FINAL_VALIDATION_CHECKLIST.md" in text
    assert "./scripts/smoke_test.sh --prod oncovax.live oncovax-operator '<password>'" in text


def test_prompt_h_makefile_has_unifying_runtime_entrypoint():
    text = MAKEFILE_PATH.read_text(encoding="utf-8")
    assert "verify-local:" in text
    verify_block = text.split("verify-local:", 1)[1]
    assert "$(COMPOSE_DEV) up -d --build" in verify_block
    assert "./scripts/smoke_test.sh" in verify_block


def test_prompt_h_checklist_covers_required_verification_surfaces_and_done_gate():
    text = CHECKLIST_PATH.read_text(encoding="utf-8")
    assert "Final Validation Checklist (Prompt H Closure)" in text
    assert "Stack-up verification" in text
    assert "Telemetry flow verification" in text
    assert "Alert generation verification" in text
    assert "Mongo/audit visibility verification" in text
    assert "Grafana population verification" in text
    assert "D2 runtime-control reaction visibility verification" in text
    assert "Cloud/live verification path (requires real infrastructure)" in text
    assert "Prompt H definition of done (release gate)" in text
    assert "not locally provable" in text


def test_prompt_h_evidence_map_links_final_closure_surfaces():
    text = EVIDENCE_MAP_PATH.read_text(encoding="utf-8")
    assert "Prompt H final closure proof surfaces" in text
    assert "docs/FINAL_VALIDATION_CHECKLIST.md" in text
    assert "Makefile" in text
    assert "verify-local" in text
    assert "Prompt H final review sequence (closure)" in text
