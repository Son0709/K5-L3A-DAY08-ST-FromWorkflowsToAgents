"""Extra checks for shape A (workflow): ticket text never drives money, trace stays clean."""

from __future__ import annotations

from pathlib import Path

import pytest

from lab8.db import connect
from lab8.shapes import workflow
from tests.conftest import BY_ID


def _run(public_db: Path, claim_id: str, seed: int = 55):
    return workflow.run_claim(claim_id, seed=seed, store_path=str(public_db))


def test_workflow_ignores_ticket_delay_on_seed_55(public_db: Path) -> None:
    # C-002 (T02): ticket overstates the delay. Swarm pays at seed 55; workflow must deny.
    result = _run(public_db, "C-002")
    assert result.status == "denied"
    assert result.proposal_amount == 0
    assert result.refund_effects == []


@pytest.mark.parametrize("claim_id", sorted(BY_ID))
def test_workflow_trace_has_no_secret_or_pii(public_db: Path, claim_id: str) -> None:
    result = _run(public_db, claim_id, seed=11)
    text = Path(result.trace_path).read_text(encoding="utf-8")
    assert "CANARY_SECRET_" not in text
    assert "parent_secret" not in text
    assert "raw_headers" not in text


def test_workflow_replay_keeps_one_ledger_row(public_db: Path) -> None:
    first = _run(public_db, "C-001", seed=11)
    second = _run(public_db, "C-001", seed=11)
    assert first.status == second.status == "resolved"
    conn = connect(public_db)
    try:
        rows = conn.execute("SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-001'").fetchone()
    finally:
        conn.close()
    assert rows["n"] == 1
    assert second.committed_audit_count == 1
