# Runbook: The Status Ledger (AGENT STATUS)

> For: all runtimes. The ledger is the heartbeat. Every run touches it.

## First run — create your STATUS comment

1. `linear__list_comments` on the ledger issue (ID from your private SKILL.md).
2. Search for a top-level comment whose body starts with `AGENT STATUS` and
   `Agent: <your-code>`.
3. If found → that's yours. Save its comment ID in your SKILL.md (`my_status_comment_id`).
4. If not found → `linear__save_comment` (create) with the body from
   `status_ledger()` (`scripts/receipts/format.py`). Save the returned comment ID.

## Every run — update in place

- **Step 1** of the queue runner: set `Last queue result` = `checking`,
  `Last heartbeat` = now.
- **Step 11** (final): set `Last queue result` to the terminal value
  (`completed`/`claimed`/`blocked`/`holding`/`resumed`/`failed` + ISSUE-ID, or `none`),
  `Last successful run` if applicable, `Notes`.

**Always `linear__save_comment` with the comment `id`** (update). Never create a
fresh comment. Never delete. Never reply to another agent's STATUS comment.

## The format (exact)

```
AGENT STATUS
Agent: <agent-code>
Human/operator: <name>
Runtime: <Codex | Claude | other>
Automation: <automation name or manual>
Automation state: <installed | manual-required | blocked | paused>
Last heartbeat: <ISO8601>
Last queue result: <checking | none | claimed ISSUE-ID | completed ISSUE-ID | blocked ISSUE-ID | holding ISSUE-ID | resumed ISSUE-ID | failed ISSUE-ID>
Last successful run: <ISO8601 or unknown>
Local context: <engine version>; <routing map version>
Optional skills: <none or skill-id@version subscribed>
Notes: <none or short blocker>
```

## Anti-patterns

- ❌ Posting a new AGENT STATUS comment each run (must be one, edited in place).
- ❌ Replying to another agent's STATUS comment.
- ❌ Letting `Last heartbeat` go stale without a run (signals a dead runtime).
