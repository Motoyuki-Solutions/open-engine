# Runbook: Optional Standing Skills (SUBSCRIBED / INSTALLED / UPDATED / DECLINED)

> For: all runtimes. The 4 skill receipts govern the optional-skill lifecycle.
> First install needs human approval in the runtime's agent thread.

## The lifecycle

```
(discovered in directory) → AGENT HUMAN HOLD (ask approval) → human answers
  → AGENT SKILL SUBSCRIBED → AGENT SKILL INSTALLED
  → (later, same-scope update) → AGENT SKILL UPDATED   [automatic]
  → (scope expansion) → fresh HUMAN HOLD → SUBSCRIBED → INSTALLED
  → (human declines) → AGENT SKILL DECLINED
```

## AGENT SKILL SUBSCRIBED — human approved first install

Posted after the human approves the first install/adaptation of an optional skill
(approval given via `AGENT HUMAN ANSWERED` on a preceding `AGENT HUMAN HOLD`):
```
AGENT SKILL SUBSCRIBED
Agent: <your-code>
Run context: <thread-id>, model <model>
Timestamp: <ISO8601>
Skill: <skill-id>@<version>
Scope: <local | team | …>
Approval basis: human-approved in agent thread
Subscribed to future same-scope updates. Scope expansion needs fresh approval.
```
- Label: `AGENT SKILL SUBSCRIBED`. No status change. Update ledger `Optional skills`.

## AGENT SKILL INSTALLED — actually installed locally

Posted after the runtime actually installs/adapts the skill locally:
```
AGENT SKILL INSTALLED
Agent: <your-code>
Run context: <thread-id>, model <model>
Timestamp: <ISO8601>
Skill: <skill-id>@<version>
Scope: <scope>
Action: installed
```
- Label: `AGENT SKILL INSTALLED`. No status change.

## AGENT SKILL UPDATED — same-scope auto-update

Posted automatically at step 3 preflight when a subscribed skill has a newer
same-scope version:
```
AGENT SKILL UPDATED
Agent: <your-code>
Run context: <thread-id>, model <model>
Timestamp: <ISO8601>
Skill: <skill-id>@<new-version>
Scope: <scope> (same-scope auto-update)
Update applied locally: adapted
```
- Label: `AGENT SKILL UPDATED`. No status change. Update ledger `Optional skills`.

## AGENT SKILL DECLINED — human declined/deferred

Posted when the human declines or defers an optional skill:
```
AGENT SKILL DECLINED
Agent: <your-code>
Run context: <thread-id>, model <model>
Timestamp: <ISO8601>
Skill: <skill-id>@<version>
Scope: <scope>
Declined/deferred: <reason>
```
- Label: `AGENT SKILL DECLINED`. No status change.

## Hard rules

- ❌ Never install a new (not-yet-subscribed) skill on a routine run. Route through HOLD.
- ❌ Never auto-apply a scope expansion. Fresh approval required.
- ❌ Never skip SUBSCRIBED and jump to INSTALLED — the approval record matters.
