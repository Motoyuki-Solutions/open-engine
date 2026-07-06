# Runbook: Unrecoverable Failure (AGENT FAILED)

> For: all execution runtimes. Triggered at queue-runner step 10.
> Use ONLY for genuine unrecoverable failures — not for blockers (see `block.md`).

## When to use AGENT FAILED

The run failed in a way that is **not** a blocked question and **not** a human-hold
decision — a real execution failure (API errors after retries, corrupted state,
unrecoverable exception). If a question would unblock you, that's `AGENT BLOCKED`.

## The three-part write

```
AGENT FAILED
Agent: <your-code>
Run context: <thread-id>, model <model>
Timestamp: <ISO8601>
Failure: <why the run could not complete>
Last safe step: <the last point at which state was consistent/committed>
Retry count: <number of attempts before giving up>
```
- Label: `AGENT FAILED`
- Status: `Agent Review` (for human triage — not Agent Done)
- Ledger `Last queue result` = `failed <ISSUE-ID>`

**Stop.** The reviewer (Eos/Dylan) triages at `Agent Review`: revise the task, retry,
or drop it.

## Anti-patterns

- ❌ AGENT FAILED for a missing answer (use AGENT BLOCKED).
- ❌ AGENT FAILED for a needed permission (use AGENT HUMAN HOLD).
- ❌ Omitting `last safe step` (the reviewer needs to know where to resume from).
