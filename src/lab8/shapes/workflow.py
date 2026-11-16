"""Shape A — deterministic workflow. Student work.

Signature (do not change):

    run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult

Suggested steps. Money stays in code (`lab8.tools.compute_compensation`).

1. Open the store. Read the claim through `get_claim_view` (not SELECT *).
2. Missing order_id -> status `needs_info`. Do not write the ledger.
3. `lookup_order`. If not visible -> `escalated`. Do not copy phone, address, item, internal note.
4. Quote from the order row. Ignore delay numbers written in the ticket.
5. Quote amount 0 -> `denied`. Do not call issue_refund.
6. Quote amount > 0 -> `durability.issue_refund(conn, claim_id, <full quote>)`.
   Pass the FULL quote. The host checks the claim's own approval and subtracts
   what earlier claims already got for the same order (T13, T14). Do not
   subtract it yourself or the host subtracts twice.
   Auth failure or order already refunded -> `denied` (the host writes `policy_denied`).
   `proposal_amount` stays the full quote. Amount conflict -> `failed`.
7. Success -> `resolved`. One ledger row, one `refund_committed` audit.
8. Use MockLLM only to draft the reply text, if you want a model call at all.

The model must not choose the refund amount and must not commit the refund.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

import sqlite3

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import compute_compensation, get_claim_view, lookup_order, tool_cost
from lab8.trace import Trace

SHAPE = "workflow"


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _end(conn, claim_id, seed, budget, trace, status, amount, reason, draft):
    # One optional model call, only to draft reply text. Never decides money.
    complete(budget, seed=seed, purpose="draft", prompt=draft)
    trace.add("decision", {"status": status, "proposal_amount": int(amount), "reason": reason})
    return finish(
        conn,
        shape=SHAPE,
        claim_id=claim_id,
        seed=seed,
        status=status,
        proposal_amount=amount,
        budget=budget,
        trace=trace,
        error_reason=reason,
    )


def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id(SHAPE, claim_id, seed))

    # 1. Read the claim through the allowlisted view.
    budget.add_tool(tool_cost())
    claim = get_claim_view(conn, claim_id)
    if not claim.get("found"):
        trace.add("error", {"reason": "unknown_claim"})
        return finish(
            conn, shape=SHAPE, claim_id=claim_id, seed=seed, status="failed",
            proposal_amount=0, budget=budget, trace=trace, error_reason="unknown_claim",
        )

    # 2. No order id -> needs_info. Never mine the ticket for an order id.
    if not claim.get("order_id"):
        return _end(conn, claim_id, seed, budget, trace, "needs_info", 0, "missing_order_id", "needs_info")

    # 3. Order must be visible to this principal.
    budget.add_tool(tool_cost())
    view = lookup_order(conn, claim["order_id"], claim["principal_id"])
    if not view.get("visible"):
        trace.add("lookup_order", {"visible": False, "reason": view.get("reason")})
        return _end(conn, claim_id, seed, budget, trace, "escalated", 0, view.get("reason"), "escalated")
    order = view["order"]
    trace.add("lookup_order", {"visible": True, "order": order})

    # 4. Quote from the order row and current policy. Ticket text is ignored.
    budget.add_tool(tool_cost())
    quote = compute_compensation(conn, order)
    amount = int(quote["amount_vnd"])
    trace.add("quote", quote)

    # 5. Nothing owed -> denied, host not called.
    if amount <= 0:
        return _end(conn, claim_id, seed, budget, trace, "denied", 0, quote.get("reason"), "denied")

    # 6. Full quote to the host. It checks approval, per-order cap, idempotency.
    #    InjectedCrash is not caught on purpose; the trace is flushed first.
    try:
        outcome = issue_refund(conn, claim_id, amount, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    trace.add("issue_refund", {"ok": outcome["ok"], "reason": outcome["reason"], "conflict": outcome["conflict"]})
    if outcome["ok"]:
        return _end(conn, claim_id, seed, budget, trace, "resolved", amount, None, f"proposal={amount}")
    status = "failed" if outcome["conflict"] else "denied"
    return _end(conn, claim_id, seed, budget, trace, status, amount, outcome["reason"], status)
