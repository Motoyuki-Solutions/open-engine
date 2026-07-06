# Task Record Template (Canonical)

> Copy this into the Linear issue **description** when creating an Open Engine task.
> Fill §1–§6 at creation; §7 is filled by agents as work progresses.
> Field in Linear: `description`. Use `linear__save_issue` with this as `description`.

---

## Title (exact format)

```
[agent instructions][<agent-code>][task] <short outcome>
```

Examples:
- `[agent instructions][bolt][task] Stand up Open Engine repo + Linear project`
- `[agent instructions][zephyr][task] Build voice pipeline config pack`

The `agent-code` in the **second bracket** is the runtime that may claim it
(enforced by queue-runner step 7 eligibility). Use `[all agents]` only for
standing/ledger/directory issues, never for tasks.

## Required label

Every Open Engine issue carries the `agent-instructions` label. Without it, the
issue is invisible to the queue runner (eligibility check fails).

## Issue body (7-part task record)

```markdown
# [short outcome-oriented task title]

## 1. Requester
<!-- Who asked for this. Human or agent. e.g. "Eos (routing)" / "Dylan" -->

## 2. Desired outcome
<!-- What "done" looks like, as an outcome — not a task list. -->

## 3. Sources
<!-- Refs, docs, links, prior issue IDs (MOT-xx), thread IDs. State that travels. -->

## 4. Acceptance criteria
<!-- Testable definition of done. Each item verifiably true or false. -->
- [ ] ...
- [ ] ...

## 5. Boundaries
<!-- What is NOT in scope. Lines the agent must not cross. -->

## 6. Blocker rule
<!-- What to do when stuck. One of:
  - Answer belongs on Linear → AGENT BLOCKED (one question), Agent Needs Input.
  - Answer belongs in human's thread → AGENT HUMAN HOLD, Agent Needs Input.
  - Escalate to <person/agent> via <channel> and stop.
  - Try alternatives <X>, <Y>, then escalate.
-->

## 7. Receipts
<!-- Filled by agents. Check off as receipts are posted. -->
- [ ] AGENT CLAIMED — _agent / timestamp / run context_
- [ ] AGENT DONE | AGENT BLOCKED | AGENT HUMAN HOLD | AGENT FAILED — _agent / timestamp / outcome_
```

## Linear issue fields to set at creation

| Field | Value |
|-------|-------|
| `title` | `[agent instructions][<agent-code>][task] <short outcome>` |
| `description` | the 7-part body above |
| `team` | `Motoyuki-dev` |
| `project` | `Open Engine` |
| `labels` | `["agent-instructions"]` (required for eligibility) |
| `assignee` | target runtime's agent, or `null` if `Standing` |
| `state` | `Standing` (not ready) or `Agent Todo` (ready, assigned) |
| `priority` | 0–4 per urgency |
| `dueDate` | if deadline (ISO) |
| `parentId` / `blocks` / `blockedBy` | if linked (Paperclip lesson #4: parents close explicitly) |
