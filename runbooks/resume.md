# Runbook: Resume a Paused Issue (AGENT UNBLOCKED / AGENT HUMAN ANSWERED / AGENT RESUMED)

> For: all execution runtimes. Triggered at queue-runner steps 4 and 5.
> Resuming counts as your **one task issue** for the run — finish it and stop.

## Two resume paths

### Path A — was AGENT BLOCKED, answer arrived on the issue (step 5)
1. Detect: the issue carries `AGENT BLOCKED` and a new answer comment now exists on it.
2. **`AGENT UNBLOCKED`** comment + label (no status change yet):
   ```
   AGENT UNBLOCKED
   Agent: <your-code>
   Run context: <thread-id>, model <model>
   Timestamp: <ISO8601>
   Answer arrived: <summary of the answer>
   Resuming now (AGENT RESUMED to follow).
   ```
3. **`AGENT RESUMED`** comment + label + status → `Agent Working`:
   ```
   AGENT RESUMED
   Agent: <your-code>
   Run context: <thread-id>, model <model>
   Timestamp: <ISO8601>
   Resuming after: AGENT UNBLOCKED
   What changed: <answer applied; proceeding>
   ```
4. Ledger `Last queue result` = `resumed <ISSUE-ID>`.
5. Finish the issue (→ `complete.md` or `block.md` again if still stuck). **Stop.**

### Path B — was AGENT HUMAN HOLD, human answered in their thread (step 4)
1. Detect: the issue carries `AGENT HUMAN HOLD` and an `AGENT HUMAN ANSWERED` receipt
   has surfaced (the human's answer, relayed back).
2. **`AGENT HUMAN ANSWERED`** comment + label (clears the hold, no status change yet):
   ```
   AGENT HUMAN ANSWERED
   Agent: <your-code>
   Run context: <thread-id>, model <model>
   Timestamp: <ISO8601>
   Human answer: <summary>
   Hold cleared. Resuming now (AGENT RESUMED to follow).
   ```
   > Note: who physically posts `AGENT HUMAN ANSWERED` depends on the runtime —
   > often the human's own agent posts it on their behalf. Either way it appears
   > as a comment on the held issue.
3. **`AGENT RESUMED`** comment + label + status → `Agent Working`.
4. Ledger `Last queue result` = `resumed <ISSUE-ID>`.
5. Finish the issue. **Stop.**

## Anti-patterns

- ❌ Resuming without first posting UNBLOCKED (or HUMAN ANSWERED) — the audit trail
  loses the "answer arrived" event.
- ❌ Resuming more than one issue per run — steps 4/5 handle one and stop.
