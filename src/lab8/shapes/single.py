"""Shape B — one ReAct agent. Student work.

Use `lab8.runtime.run_react` with max_steps=8. `decide` may pick a read tool.
It must not call `issue_refund`. After the loop, the host validates the quote
and is the only writer.

A decide() that trusts ticket text over the order row will fail hidden claims
where the customer overstates the delay or cites a superseded clause.

Per-order cap: an order may already have been refunded by an earlier claim.
The read tool `lookup_refund_history` shows how much. The host still enforces
the cap, so pass the full quote to `durability.issue_refund`, not a net amount.

Caps: stop at 8 steps. Count model calls in the Budget so cost stays comparable.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import get_claim_view, tool_cost
from lab8.trace import Trace

SHAPE = "single"
MAX_STEPS = 8


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


def _make_decide(budget: Budget, trace: Trace, seed: int):
    """Scripted policy standing in for the model: read tools only, never issue_refund.

    run_react replaces the observation each step, so facts gathered so far live here.
    The ticket is never read; delay and fee come from the order row only.
    """
    memory: dict[str, Any] = {}

    def decide(seen: dict[str, Any]) -> dict[str, Any]:
        # One simulated model call per step. Prompt carries no ticket text.
        complete(budget, seed=seed, purpose="plan", prompt=f"step={len(memory)} last={seen.get('last_tool')}")
        claim = seen.get("claim") or {}
        last, result = seen.get("last_tool"), seen.get("last_result")
        if last == "lookup_order":
            memory["order_view"] = result
            trace.add("lookup_order", {"visible": result.get("visible"), "reason": result.get("reason"), "order": result.get("order")})
        elif last == "lookup_refund_history":
            memory["history"] = result
            trace.add("lookup_refund_history", {k: result.get(k) for k in ("visible", "refund_count", "refunded_vnd")})
        elif last == "compute_compensation":
            memory["quote"] = result
            trace.add("quote", result)

        if not claim.get("order_id"):
            return {"final": {"status": "needs_info", "error_reason": "missing_order_id"}}
        if "order_view" not in memory:
            return {"tool": "lookup_order", "args": {"order_id": claim["order_id"], "principal_id": claim["principal_id"]}}
        view = memory["order_view"]
        if not view.get("visible"):
            return {"final": {"status": "escalated", "error_reason": view.get("reason")}}
        if "history" not in memory:
            return {"tool": "lookup_refund_history", "args": {"order_id": claim["order_id"], "principal_id": claim["principal_id"]}}
        if "quote" not in memory:
            return {"tool": "compute_compensation", "args": {"order": view["order"]}}
        quote = memory["quote"]
        return {"final": {"status": "quote", "amount": int(quote["amount_vnd"]), "error_reason": quote.get("reason")}}

    return decide


def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id(SHAPE, claim_id, seed))

    budget.add_tool(tool_cost())
    claim = get_claim_view(conn, claim_id)
    if not claim.get("found"):
        trace.add("error", {"reason": "unknown_claim"})
        return finish(
            conn, shape=SHAPE, claim_id=claim_id, seed=seed, status="failed",
            proposal_amount=0, budget=budget, trace=trace, error_reason="unknown_claim",
        )
    # Observation keeps only the allowlisted view; the ticket text is dropped.
    observation = {"claim": {k: claim[k] for k in ("claim_id", "principal_id", "order_id")}}

    loop = run_react(
        conn, budget, observation=observation,
        decide=_make_decide(budget, trace, seed), max_steps=MAX_STEPS,
    )
    final = loop["final"]
    trace.add("react_end", {"stopped": loop["stopped"], "status": final.get("status")})

    def end(status: str, amount: int, reason: str | None) -> RunResult:
        complete(budget, seed=seed, purpose="draft", prompt=f"{status}:{amount}")
        trace.add("decision", {"status": status, "proposal_amount": int(amount), "reason": reason})
        return finish(
            conn, shape=SHAPE, claim_id=claim_id, seed=seed, status=status,
            proposal_amount=amount, budget=budget, trace=trace, error_reason=reason,
        )

    status = final.get("status")
    if status != "quote":
        return end(status, 0, final.get("error_reason"))

    amount = int(final["amount"])
    if amount <= 0:
        return end("denied", 0, final.get("error_reason"))

    # Host is the only writer. Full quote, crash_at passed through, InjectedCrash not swallowed.
    try:
        outcome = issue_refund(conn, claim_id, amount, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise
    trace.add("issue_refund", {"ok": outcome["ok"], "reason": outcome["reason"], "conflict": outcome["conflict"]})
    if outcome["ok"]:
        return end("resolved", amount, None)
    return end("failed" if outcome["conflict"] else "denied", amount, outcome["reason"])
