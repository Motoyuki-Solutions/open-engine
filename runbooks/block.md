# Runbook: Handle a Blocker (AGENT BLOCKED / AGENT HUMAN HOLD)

> For: all execution runtimes. Triggered at queue-runner step 9.
> First: follow the task record's §6 Blocker rule. This runbook is the default behavior.

## The key decision: where does the answer belong?

| Answer belongs… | Receipt | Ledger result |
|-----------------|---------|---------------|
| **On the Linear issue** (a factual question about the task) | `AGENT BLOCKED` | `blocked ISSUE-ID` |
| **In the human's own agent thread/app** (a permission, preference, or decision only they can make) | `AGENT HUMAN HOLD` | `holding ISSUE-ID` |

`AGENT BLOCKED` asks **one question** on the issue. `AGENT HUMAN HOLD` asks in the
human's thread because the answer shouldn't live in Linear (e.g. "approve this skill
install", "pick option A or B for your account").

## AGENT BLOCKED — three-part write

```
AGENT BLOCKED
Agent: <your-code>
Run context: <thread-id>, model <model>
Timestamp: <ISO8601>
Question: <the one question, answerable on this issue>
Answer belongs: on this Linear issue (one question, one answer).
Context: <what you tried / where you are>
```
- Label: `AGENT BLOCKED`
- Status: `Agent Needs Input`
- Ledger: `Last queue result` = `blocked <ISSUE-ID>`

**Stop.** The answer arrives as a comment on the same issue; your next run's step 5
detects it and you post `AGENT UNBLOCKED` → `AGENT RESUMED` → finish.

## AGENT HUMAN HOLD — three-part write

```
AGENT HUMAN HOLD
Agent: <your-code>
Run context: <thread-id>, model <model>
Timestamp: <ISO8601>
Need from human: <the specific permission/decision>
Why this belongs in your thread (not Linear): <reason>
Answer with AGENT HUMAN ANSWERED in your agent thread.
```
- Label: `AGENT HUMAN HOLD`
- Status: `Agent Needs Input`
- Ledger: `Last queue result` = `holding <ISSUE-ID>`

**Stop.** The human answers in their thread; the answer surfaces as
`AGENT HUMAN ANSWERED`; your next run's step 4 detects it and you post
`AGENT RESUMED` → finish.

## Resuming (steps 4/5 of the next run)

When the blocker clears:
- `AGENT UNBLOCKED` (for BLOCKED) **then** `AGENT RESUMED` — move to `Agent Working`.
- `AGENT HUMAN ANSWERED` (posted by the human path) **then** `AGENT RESUMED` — move to `Agent Working`.
- Ledger `Last queue result` = `resumed <ISSUE-ID>`.

See `resume.md` for the full resume flow.

## Anti-patterns

- ❌ Silently stopping with no receipt.
- ❌ Asking multiple questions in one AGENT BLOCKED (one question only).
- ❌ Using AGENT BLOCKED when the answer belongs in the human's thread (use HOLD).
- ❌ Using AGENT FAILED for a blocker (FAILED = unrecoverable; BLOCKED = waiting).
