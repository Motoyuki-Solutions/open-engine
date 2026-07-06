#!/usr/bin/env python3
"""
Open Engine — state machine (canonical v2).

Maps each receipt token to the Linear writes it implies, grouped by category:
  - task-lifecycle
  - standing-context
  - skill
  - delegation
  - ledger (special: in-place comment, no label, no status change)

Implements the canonical queue-runner state machine. See
templates/queue-runner-prompt.md for the exact 11-step ordered process.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from receipts.format import TOKENS, LABEL_COLORS, LABEL_NAMES  # noqa: E402


# ---------------------------------------------------------------------------
# Linear statuses (canonical Open Engine set).
# ---------------------------------------------------------------------------
STATUSES = {
    "Standing":            "backlog",     # exists but not yet assignable
    "Agent Todo":          "unstarted",   # eligible to be claimed
    "Agent Working":       "started",     # claimed, in progress
    "Agent Needs Input":   "started",     # blocked / human hold
    "Agent Review":        "started",     # done, awaiting acceptance
    "Agent Done":          "completed",   # accepted
}

# Canonical agent-instructions label.
AGENT_INSTRUCTIONS_LABEL = "agent-instructions"


# ---------------------------------------------------------------------------
# Transition table: receipt -> (label, target_status, ledger_queue_result)
# ledger_queue_result is what the runner writes to the AGENT STATUS ledger's
# "Last queue result" field. None means "leave ledger as-is" (e.g. sub-receipts).
# ---------------------------------------------------------------------------
TRANSITIONS = {
    # --- task-lifecycle ---
    "AGENT CLAIMED": {
        "category": "task-lifecycle",
        "label": LABEL_NAMES['AGENT CLAIMED'],
        "target_status": "Agent Working",
        "ledger_result": "claimed",   # + ISSUE-ID
        "order": [  # three-part write
            "comment",  # AGENT CLAIMED
            "label",    # append AGENT CLAIMED
            "status",   # Agent Working
        ],
    },
    "AGENT DONE": {
        "category": "task-lifecycle",
        "label": LABEL_NAMES['AGENT DONE'],
        # target_status chosen by caller: "Agent Done" or "Agent Review"
        "target_status": None,  # caller decides based on review-needs
        "ledger_result": "completed",  # + ISSUE-ID
        "order": ["comment", "label", "status"],
    },
    "AGENT BLOCKED": {
        "category": "task-lifecycle",
        "label": LABEL_NAMES['AGENT BLOCKED'],
        "target_status": "Agent Needs Input",
        "ledger_result": "blocked",  # + ISSUE-ID
        "order": ["comment", "label", "status"],
    },
    "AGENT UNBLOCKED": {
        "category": "task-lifecycle",
        "label": LABEL_NAMES['AGENT UNBLOCKED'],
        "target_status": None,  # no status change; precedes AGENT RESUMED
        "ledger_result": None,
        "order": ["comment", "label"],  # status set by the following RESUMED
    },
    "AGENT HUMAN HOLD": {
        "category": "task-lifecycle",
        "label": LABEL_NAMES['AGENT HUMAN HOLD'],
        "target_status": "Agent Needs Input",
        "ledger_result": "holding",  # + ISSUE-ID
        "order": ["comment", "label", "status"],
    },
    "AGENT HUMAN ANSWERED": {
        "category": "task-lifecycle",
        "label": LABEL_NAMES['AGENT HUMAN ANSWERED'],
        "target_status": None,  # clears the hold; RESUMED follows
        "ledger_result": None,
        "order": ["comment", "label"],
    },
    "AGENT RESUMED": {
        "category": "task-lifecycle",
        "label": LABEL_NAMES['AGENT RESUMED'],
        "target_status": "Agent Working",
        "ledger_result": "resumed",  # + ISSUE-ID
        "order": ["comment", "label", "status"],
    },
    "AGENT FAILED": {
        "category": "task-lifecycle",
        "label": LABEL_NAMES['AGENT FAILED'],
        "target_status": "Agent Review",  # for triage
        "ledger_result": "failed",  # + ISSUE-ID
        "order": ["comment", "label", "status"],
    },

    # --- standing-context ---
    "AGENT APPLIED": {
        "category": "standing-context",
        "label": LABEL_NAMES['AGENT APPLIED'],
        "target_status": None,  # standing issues don't move on apply
        "ledger_result": None,
        "order": ["comment", "label"],
    },

    # --- skill ---
    "AGENT SKILL SUBSCRIBED": {
        "category": "skill",
        "label": LABEL_NAMES['AGENT SKILL SUBSCRIBED'],
        "target_status": None,
        "ledger_result": None,
        "order": ["comment", "label"],
    },
    "AGENT SKILL INSTALLED": {
        "category": "skill",
        "label": LABEL_NAMES['AGENT SKILL INSTALLED'],
        "target_status": None,
        "ledger_result": None,
        "order": ["comment", "label"],
    },
    "AGENT SKILL UPDATED": {
        "category": "skill",
        "label": LABEL_NAMES['AGENT SKILL UPDATED'],
        "target_status": None,
        "ledger_result": None,
        "order": ["comment", "label"],
    },
    "AGENT SKILL DECLINED": {
        "category": "skill",
        "label": LABEL_NAMES['AGENT SKILL DECLINED'],
        "target_status": None,
        "ledger_result": None,
        "order": ["comment", "label"],
    },

    # --- delegation ---
    "AGENT FOLLOW-UP": {
        "category": "delegation",
        "label": "AGENT FOLLOW-UP",
        "target_status": None,  # posted on the delegating agent's own issue
        "ledger_result": None,
        "order": ["comment", "label"],
    },

    # --- ledger ---
    "AGENT STATUS": {
        "category": "ledger",
        "label": LABEL_NAMES["AGENT STATUS"],  # agent-status label exists
        "target_status": None,   # NO status change — ledger issue stays Standing
        "ledger_result": None,   # this IS the ledger
        "order": ["comment_inplace"],  # edit the existing comment in place, never append
    },
}


# Sanity: every token has a transition.
_missing = [t for t in TOKENS if t not in TRANSITIONS]
assert not _missing, f"Missing transitions for: {_missing}"


def writes_for_receipt(kind: str, *, review_needed: bool = False) -> dict:
    """Return the Linear writes implied by posting a receipt of `kind`.

    For AGENT DONE, pass review_needed=True to target Agent Review instead of
    Agent Done (per runner step 8).
    """
    kind = kind.upper().strip()
    if kind not in TRANSITIONS:
        raise ValueError(f"Unknown receipt token: {kind}")

    t = TRANSITIONS[kind]
    target = t["target_status"]
    if kind == "AGENT DONE":
        target = "Agent Review" if review_needed else "Agent Done"

    return {
        "category": t["category"],
        "label": t["label"],           # None for STATUS
        "target_status": target,       # None if no status change
        "ledger_result": t["ledger_result"],
        "write_order": t["order"],
    }


def three_part_write_summary(issue_id: str, kind: str, *, review_needed: bool = False) -> str:
    """Human-readable summary of the writes an agent makes for a receipt."""
    w = writes_for_receipt(kind, review_needed=review_needed)
    label_part = f", labels=[{w['label']}]" if w["label"] else ""
    status_part = f', state="{w["target_status"]}"' if w["target_status"] else ""
    ledger_part = (
        f"  -> ledger Last queue result: {w['ledger_result']} {issue_id}\n"
        if w["ledger_result"] else ""
    )

    if w["write_order"] == ["comment_inplace"]:
        return (
            f"In-place write for {kind} on ledger issue:\n"
            f"  linear__save_comment(id=<existing AGENT STATUS comment id>, body=<updated ledger>)\n"
            f"  (NO label, NO status change — edit the same comment every run)\n"
        )

    steps = []
    n = 1
    for op in w["write_order"]:
        if op == "comment":
            steps.append(f"  {n}. linear__save_comment(issueId={issue_id}, body=<{kind} receipt>)")
        elif op == "label":
            steps.append(f"  {n}. linear__save_issue(id={issue_id}{label_part})  # append label")
        elif op == "status":
            steps.append(f"  {n}. linear__save_issue(id={issue_id}{status_part})  # PATCH STATUS")
        n += 1
    if ledger_part:
        steps.append(ledger_part.rstrip())

    return f"Three-part write for {kind} on {issue_id} [{w['category']}]:\n" + "\n".join(steps) + "\n"


# ---------------------------------------------------------------------------
# Eligibility check for step 7 of the queue runner.
# ---------------------------------------------------------------------------
def is_eligible_for_claim(issue: dict, agent_code: str) -> bool:
    """Runner step 7 eligibility:
       - label includes agent-instructions
       - title contains '[agent instructions]'
       - title's second bracket == this runtime's agent code
       - status is Agent Todo
    """
    labels = [l.get("name", "") for l in issue.get("labels", [])]
    if AGENT_INSTRUCTIONS_LABEL not in labels:
        return False
    title = issue.get("title", "")
    if "[agent instructions]" not in title.lower():
        return False
    # Second bracket token must equal the agent code.
    brackets = _extract_brackets(title)
    if len(brackets) < 2 or brackets[1].lower() != agent_code.lower():
        return False
    state = (issue.get("state") or {}).get("name", "")
    return state == "Agent Todo"


def _extract_brackets(title: str) -> list:
    """Extract [bracket] tokens from a title, in order."""
    out = []
    cur = ""
    inside = False
    for ch in title:
        if ch == "[":
            inside = True
            cur = ""
        elif ch == "]" and inside:
            out.append(cur.strip())
            inside = False
        elif inside:
            cur += ch
    return out


if __name__ == "__main__":
    print("=" * 70)
    print("Open Engine state machine — receipts by category")
    print("=" * 70)
    cats = {}
    for k, v in TRANSITIONS.items():
        cats.setdefault(v["category"], []).append(k)
    for cat in ["task-lifecycle", "standing-context", "skill", "delegation", "ledger"]:
        print(f"\n[{cat}]  ({len(cats[cat])} tokens)")
        for k in cats[cat]:
            t = TRANSITIONS[k]
            tgt = t["target_status"] or "(no status change)"
            lbl = t["label"] or "(no label)"
            lr = t["ledger_result"] or "(no ledger update)"
            print(f"  {k:<26} -> label={lbl:<26} status={tgt:<20} ledger={lr}")

    print("\n" + "=" * 70)
    print("Sample three-part writes")
    print("=" * 70)
    for k in ["AGENT CLAIMED", "AGENT DONE", "AGENT BLOCKED", "AGENT HUMAN HOLD",
              "AGENT RESUMED", "AGENT FAILED", "AGENT APPLIED",
              "AGENT SKILL SUBSCRIBED", "AGENT FOLLOW-UP", "AGENT STATUS"]:
        print(three_part_write_summary("MOT-7", k))
    print(three_part_write_summary("MOT-7", "AGENT DONE", review_needed=True))

    print("=" * 70)
    print("Eligibility check (step 7)")
    print("=" * 70)
    samples = [
        ({"title": "[agent instructions][bolt][task] stand up repo",
          "labels": [{"name": "agent-instructions"}],
          "state": {"name": "Agent Todo"}}, "bolt", True),
        ({"title": "[agent instructions][zephyr][task] build thing",
          "labels": [{"name": "agent-instructions"}],
          "state": {"name": "Agent Todo"}}, "bolt", False),   # wrong agent code
        ({"title": "[agent instructions][bolt][task] stand up repo",
          "labels": [{"name": "agent-instructions"}],
          "state": {"name": "Agent Working"}}, "bolt", False),  # already claimed
        ({"title": "stand up repo",  # missing brackets/label
          "labels": [{"name": "Bug"}],
          "state": {"name": "Agent Todo"}}, "bolt", False),
    ]
    for i, (issue, code, expected) in enumerate(samples, 1):
        got = is_eligible_for_claim(issue, code)
        ok = "OK" if got == expected else "FAIL"
        print(f"  sample {i}: eligible={got}  expected={expected}  [{ok}]  title={issue['title']!r} agent={code}")

    print(f"\nTotal receipt tokens: {len(TOKENS)} (canonical spec = 15)")
