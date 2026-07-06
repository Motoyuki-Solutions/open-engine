#!/usr/bin/env python3
"""
Open Engine — receipt comment formatters (canonical v2).

All 15 canonical receipt tokens + the AGENT STATUS ledger comment.
Agents call `receipt()` to build a comment body before posting via
linear__save_comment. Keeping the format in one place guarantees the
vocabulary stays consistent and the audit log stays greppable.

Receipt categories:
  - task-lifecycle : CLAIMED, DONE, BLOCKED, UNBLOCKED, HUMAN HOLD,
                     HUMAN ANSWERED, RESUMED, FAILED
  - standing-context : APPLIED
  - skill : SKILL SUBSCRIBED, SKILL INSTALLED, SKILL UPDATED, SKILL DECLINED
  - delegation : FOLLOW-UP
  - ledger : STATUS (single comment updated in place, never appended)

Reference: canonical Open Engine spec (Nate Jones, v2), routed by Eos.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional


# ---------------------------------------------------------------------------
# The 15 canonical receipt tokens (exact strings).
# ---------------------------------------------------------------------------
TOKENS = {
    # task-lifecycle
    "AGENT CLAIMED":          "Agent picked up the task; the claim lock",
    "AGENT DONE":             "Scoped work finished (Agent Done or Agent Review)",
    "AGENT BLOCKED":          "Answer belongs on the Linear issue; one question",
    "AGENT UNBLOCKED":        "A blocked issue's answer arrived; precedes RESUMED",
    "AGENT HUMAN HOLD":       "Answer belongs in human's own agent thread/app",
    "AGENT HUMAN ANSWERED":   "Human answered a hold in their thread; clears hold",
    "AGENT RESUMED":          "Continuing a paused issue after UNBLOCKED/ANSWERED",
    "AGENT FAILED":           "Unrecoverable failure; last safe step + retry count",
    # standing-context
    "AGENT APPLIED":          "Runtime installed/adapted a standing context version locally",
    # skill
    "AGENT SKILL SUBSCRIBED": "Human approved first install/adaptation of optional skill",
    "AGENT SKILL INSTALLED":  "Runtime actually installed/adapted an optional skill",
    "AGENT SKILL UPDATED":    "Subscribed optional skill got a same-scope local update",
    "AGENT SKILL DECLINED":   "Human declined/deferred an optional standing skill",
    # delegation
    "AGENT FOLLOW-UP":        "A delegated issue's state changed",
    # ledger
    "AGENT STATUS":           "The single ledger comment each agent updates in place",
}

# Linear label NAME per token. The receipt *comment body* uses the uppercase
# token (e.g. "AGENT CLAIMED"); the Linear *label* is lowercase kebab-case
# (e.g. "agent-claimed"). These are two different artifacts.
LABEL_NAMES = {
    "AGENT CLAIMED":          "agent-claimed",
    "AGENT DONE":             "agent-done",
    "AGENT BLOCKED":          "agent-blocked",
    "AGENT UNBLOCKED":        "agent-unblocked",
    "AGENT HUMAN HOLD":       "agent-human-hold",
    "AGENT HUMAN ANSWERED":   "agent-human-answered",
    "AGENT RESUMED":          "agent-resumed",
    "AGENT FAILED":           "agent-failed",
    "AGENT APPLIED":          "agent-applied",
    "AGENT SKILL SUBSCRIBED": "agent-skill-subscribed",
    "AGENT SKILL INSTALLED":  "agent-skill-installed",
    "AGENT SKILL UPDATED":    "agent-skill-updated",
    "AGENT SKILL DECLINED":   "agent-skill-declined",
    "AGENT FOLLOW-UP":        "agent-follow-up",
    "AGENT STATUS":           "agent-status",
}

# Linear label color per token.
LABEL_COLORS = {
    "AGENT CLAIMED":          "#4EA7FC",  # blue
    "AGENT DONE":             "#2ECC71",  # green
    "AGENT BLOCKED":          "#EB5757",  # red
    "AGENT UNBLOCKED":        "#2ECC71",  # green (answer arrived)
    "AGENT HUMAN HOLD":       "#F5C14B",  # amber
    "AGENT HUMAN ANSWERED":   "#F5C14B",  # amber (clears hold)
    "AGENT RESUMED":          "#BB87FC",  # purple
    "AGENT FAILED":           "#8993A5",  # grey
    "AGENT APPLIED":          "#00C7B7",  # teal (standing context)
    "AGENT SKILL SUBSCRIBED": "#7C5CFF",  # indigo
    "AGENT SKILL INSTALLED":  "#7C5CFF",  # indigo
    "AGENT SKILL UPDATED":    "#7C5CFF",  # indigo
    "AGENT SKILL DECLINED":   "#8993A5",  # grey
    "AGENT FOLLOW-UP":        "#5E6AD2",  # linear-blue (delegation)
    "AGENT STATUS":           "#5E6AD2",  # linear-blue (ledger) — agent-status label exists
}


def receipt(
    kind: str,
    *,
    agent: str,
    thread_id: str,
    model: str,
    ts: Optional[str] = None,
    # task-lifecycle fields
    plan: Optional[str] = None,
    outcome: Optional[str] = None,
    evidence: Optional[list] = None,
    question: Optional[str] = None,          # AGENT BLOCKED: the one question
    context: Optional[str] = None,           # AGENT BLOCKED: what was tried/where
    answer_summary: Optional[str] = None,    # AGENT UNBLOCKED / HUMAN ANSWERED
    need: Optional[str] = None,              # AGENT HUMAN HOLD: what's needed
    why: Optional[str] = None,               # AGENT HUMAN HOLD: why not on Linear
    resuming_after: Optional[str] = None,    # AGENT RESUMED
    what_changed: Optional[str] = None,      # AGENT RESUMED
    last_safe_step: Optional[str] = None,    # AGENT FAILED
    retry_count: Optional[int] = None,       # AGENT FAILED
    failure_reason: Optional[str] = None,    # AGENT FAILED
    # standing-context
    context_version: Optional[str] = None,   # AGENT APPLIED
    installed_locally: Optional[str] = None, # AGENT APPLIED: what changed locally
    # skill fields
    skill_id: Optional[str] = None,
    skill_version: Optional[str] = None,
    skill_scope: Optional[str] = None,
    skill_action: Optional[str] = None,      # installed / adapted / updated / declined
    approval_basis: Optional[str] = None,    # SKILL SUBSCRIBED
    decline_reason: Optional[str] = None,    # SKILL DECLINED
    # delegation
    delegated_issue: Optional[str] = None,   # AGENT FOLLOW-UP
    state_change: Optional[str] = None,      # AGENT FOLLOW-UP
) -> str:
    """Format a receipt comment body for the given token kind."""
    kind = kind.upper().strip()
    if kind not in TOKENS:
        raise ValueError(
            f"Unknown receipt token: {kind!r}. Valid: {sorted(TOKENS)}"
        )

    ts = ts or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    run_ctx = f"Hyperagent thread {thread_id}, model {model}"

    lines = [kind, f"Agent: {agent}", f"Run context: {run_ctx}", f"Timestamp: {ts}"]

    if kind == "AGENT CLAIMED":
        if plan is None:
            raise ValueError("AGENT CLAIMED requires `plan`")
        lines.append(f"Plan: {plan}")

    elif kind == "AGENT DONE":
        if outcome is None:
            raise ValueError("AGENT DONE requires `outcome`")
        lines.append(f"Outcome: {outcome}")
        if evidence:
            lines.append("Evidence:")
            lines.extend(f"  - {e}" for e in evidence)
        lines.append("Scoped work complete. Ready for review/acceptance per acceptance criteria.")

    elif kind == "AGENT BLOCKED":
        if question is None:
            raise ValueError("AGENT BLOCKED requires `question` (the one question to answer on this issue)")
        lines.append(f"Question: {question}")
        lines.append("Answer belongs: on this Linear issue (one question, one answer).")
        if context:
            lines.append(f"Context: {context}")

    elif kind == "AGENT UNBLOCKED":
        if answer_summary is None:
            raise ValueError("AGENT UNBLOCKED requires `answer_summary`")
        lines.append(f"Answer arrived: {answer_summary}")
        lines.append("Resuming now (AGENT RESUMED to follow).")

    elif kind == "AGENT HUMAN HOLD":
        if need is None or why is None:
            raise ValueError("AGENT HUMAN HOLD requires `need` and `why`")
        lines.append(f"Need from human: {need}")
        lines.append(f"Why this belongs in your thread (not Linear): {why}")
        lines.append("Answer with AGENT HUMAN ANSWERED in your agent thread.")

    elif kind == "AGENT HUMAN ANSWERED":
        if answer_summary is None:
            raise ValueError("AGENT HUMAN ANSWERED requires `answer_summary`")
        lines.append(f"Human answer: {answer_summary}")
        lines.append("Hold cleared. Resuming now (AGENT RESUMED to follow).")

    elif kind == "AGENT RESUMED":
        if resuming_after is None or what_changed is None:
            raise ValueError("AGENT RESUMED requires `resuming_after` and `what_changed`")
        lines.append(f"Resuming after: {resuming_after}")
        lines.append(f"What changed: {what_changed}")

    elif kind == "AGENT FAILED":
        if failure_reason is None or last_safe_step is None or retry_count is None:
            raise ValueError("AGENT FAILED requires `failure_reason`, `last_safe_step`, `retry_count`")
        lines.append(f"Failure: {failure_reason}")
        lines.append(f"Last safe step: {last_safe_step}")
        lines.append(f"Retry count: {retry_count}")

    elif kind == "AGENT APPLIED":
        if context_version is None:
            raise ValueError("AGENT APPLIED requires `context_version`")
        lines.append(f"Standing context version: {context_version}")
        lines.append(f"Installed/adapted locally: {installed_locally or '(no local change)'}")

    elif kind == "AGENT SKILL SUBSCRIBED":
        if skill_id is None:
            raise ValueError("AGENT SKILL SUBSCRIBED requires `skill_id`")
        lines.append(f"Skill: {skill_id}@{skill_version or 'n/a'}")
        lines.append(f"Scope: {skill_scope or 'unspecified'}")
        lines.append(f"Approval basis: {approval_basis or 'human-approved in agent thread'}")
        lines.append("Subscribed to future same-scope updates. Scope expansion needs fresh approval.")

    elif kind == "AGENT SKILL INSTALLED":
        if skill_id is None:
            raise ValueError("AGENT SKILL INSTALLED requires `skill_id`")
        lines.append(f"Skill: {skill_id}@{skill_version or 'n/a'}")
        lines.append(f"Scope: {skill_scope or 'unspecified'}")
        lines.append(f"Action: {skill_action or 'installed'}")

    elif kind == "AGENT SKILL UPDATED":
        if skill_id is None:
            raise ValueError("AGENT SKILL UPDATED requires `skill_id`")
        lines.append(f"Skill: {skill_id}@{skill_version or 'n/a'}")
        lines.append(f"Scope: {skill_scope or 'unspecified'} (same-scope auto-update)")
        lines.append(f"Update applied locally: {skill_action or 'adapted'}")

    elif kind == "AGENT SKILL DECLINED":
        if skill_id is None:
            raise ValueError("AGENT SKILL DECLINED requires `skill_id`")
        lines.append(f"Skill: {skill_id}@{skill_version or 'n/a'}")
        lines.append(f"Scope: {skill_scope or 'unspecified'}")
        lines.append(f"Declined/deferred: {decline_reason or 'not specified'}")

    elif kind == "AGENT FOLLOW-UP":
        if delegated_issue is None:
            raise ValueError("AGENT FOLLOW-UP requires `delegated_issue`")
        lines.append(f"Delegated issue: {delegated_issue}")
        lines.append(f"State change: {state_change or 'changed'}")

    elif kind == "AGENT STATUS":
        # STATUS is a single in-place ledger comment, not a receipt appended to a task.
        # Use status_ledger() instead for the full structured format.
        raise ValueError(
            "AGENT STATUS is a ledger comment built with status_ledger(), not receipt()."
        )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# AGENT STATUS — the single ledger comment (updated in place, never appended).
# ---------------------------------------------------------------------------
# Last queue result vocabulary (exact):
LEDGER_QUEUE_RESULTS = {
    "checking", "none",
    "claimed", "completed", "blocked", "holding", "resumed", "failed",
}


def status_ledger(
    *,
    agent_code: str,
    human_operator: str,
    runtime: str,                       # Codex | Claude | other
    automation: str,                    # automation name or "manual"
    automation_state: str,              # installed | manual-required | blocked | paused
    last_heartbeat: str,
    last_queue_result: str,             # one of LEDGER_QUEUE_RESULTS (+ optional ISSUE-ID)
    last_queue_issue: Optional[str] = None,  # ISSUE-ID if result references one
    last_successful_run: str = "unknown",
    engine_version: str,
    routing_map_version: str,
    optional_skills: str = "none",      # "none" or "skill-id@version subscribed"
    notes: str = "none",
) -> str:
    """Build the AGENT STATUS ledger comment body.

    Each agent owns exactly ONE top-level AGENT STATUS comment on the ledger
    issue and updates it IN PLACE every run (edit the same comment, never post
    a fresh one).
    """
    lqr = last_queue_result.lower().strip()
    if lqr not in LEDGER_QUEUE_RESULTS:
        raise ValueError(
            f"last_queue_result must be one of {sorted(LEDGER_QUEUE_RESULTS)}, got {lqr!r}"
        )
    lqr_full = f"{lqr} {last_queue_issue}" if last_queue_issue else lqr

    return "\n".join([
        "AGENT STATUS",
        f"Agent: {agent_code}",
        f"Human/operator: {human_operator}",
        f"Runtime: {runtime}",
        f"Automation: {automation}",
        f"Automation state: {automation_state}",
        f"Last heartbeat: {last_heartbeat}",
        f"Last queue result: {lqr_full}",
        f"Last successful run: {last_successful_run}",
        f"Local context: {engine_version}; {routing_map_version}",
        f"Optional skills: {optional_skills}",
        f"Notes: {notes}",
    ])


if __name__ == "__main__":
    # Self-test: print a sample of each receipt + a ledger comment.
    common = dict(agent="bolt", thread_id="cmr5pyo1x...", model="claude-opus-4-8")

    print("=== AGENT CLAIMED ===")
    print(receipt("AGENT CLAIMED", **common, plan="Scaffold repo, commit, set up Linear project + labels."))

    print("\n=== AGENT DONE ===")
    print(receipt("AGENT DONE", **common,
                  outcome="open-engine repo + Linear project + 6 labels created.",
                  evidence=["https://github.com/Motoyuki-Solutions/open-engine"]))

    print("\n=== AGENT BLOCKED ===")
    print(receipt("AGENT BLOCKED", **common,
                  question="Is the GitHub MCP connection enabled for bolt-hyperagent? (yes/no)",
                  context="Searched integrations; github shows configured:false."))

    print("\n=== AGENT UNBLOCKED ===")
    print(receipt("AGENT UNBLOCKED", **common, answer_summary="Eos confirmed GitHub OAuth authorized in thread."))

    print("\n=== AGENT HUMAN HOLD ===")
    print(receipt("AGENT HUMAN HOLD", **common,
                  need="Approve first install of the open-engine-cli optional skill.",
                  why="First install of an optional standing skill needs human approval in your thread."))

    print("\n=== AGENT HUMAN ANSWERED ===")
    print(receipt("AGENT HUMAN ANSWERED", **common, answer_summary="Dylan approved the skill install."))

    print("\n=== AGENT RESUMED ===")
    print(receipt("AGENT RESUMED", **common,
                  resuming_after="AGENT HUMAN ANSWERED",
                  what_changed="Skill approved; proceeding with install."))

    print("\n=== AGENT FAILED ===")
    print(receipt("AGENT FAILED", **common,
                  failure_reason="Linear API returned 403 on label creation 3x.",
                  last_safe_step="Project created; label loop halted on 4th label.",
                  retry_count=3))

    print("\n=== AGENT APPLIED ===")
    print(receipt("AGENT APPLIED", **common,
                  context_version="open-engine-core-v1",
                  installed_locally="Updated ~/.hermes/skills/open-engine/SKILL.md engine version v1."))

    print("\n=== AGENT SKILL SUBSCRIBED ===")
    print(receipt("AGENT SKILL SUBSCRIBED", **common,
                  skill_id="open-engine-cli", skill_version="v1", skill_scope="local"))

    print("\n=== AGENT SKILL INSTALLED ===")
    print(receipt("AGENT SKILL INSTALLED", **common,
                  skill_id="open-engine-cli", skill_version="v1", skill_scope="local",
                  skill_action="installed"))

    print("\n=== AGENT SKILL UPDATED ===")
    print(receipt("AGENT SKILL UPDATED", **common,
                  skill_id="open-engine-cli", skill_version="v1.1", skill_scope="local"))

    print("\n=== AGENT SKILL DECLINED ===")
    print(receipt("AGENT SKILL DECLINED", **common,
                  skill_id="open-engine-cli", skill_version="v1", skill_scope="local",
                  decline_reason="Dylan deferred; will revisit next quarter."))

    print("\n=== AGENT FOLLOW-UP ===")
    print(receipt("AGENT FOLLOW-UP", **common,
                  delegated_issue="MOT-14", state_change="moved to Agent Done by zephyr"))

    print("\n=== AGENT STATUS (ledger) ===")
    print(status_ledger(
        agent_code="bolt",
        human_operator="dylan",
        runtime="Claude",
        automation="hyperagent-live",
        automation_state="installed",
        last_heartbeat="2026-07-04T06:20:00Z",
        last_queue_result="completed",
        last_queue_issue="MOT-7",
        last_successful_run="2026-07-04T06:20:00Z",
        engine_version="open-engine-core-v1",
        routing_map_version="routing-map-v1",
        optional_skills="none",
        notes="none",
    ))

    print("\n=== TOKEN COUNT ===")
    print(f"{len(TOKENS)} receipt tokens defined (canonical spec = 15).")
