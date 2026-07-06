# Runbook: Claim a Task (AGENT CLAIMED)

> For: all execution runtimes (Bolt, Zephyr). Triggered at queue-runner step 7.
> Prereq: steps 1–6 of the queue runner found nothing to resume/delegate.

## When to claim

Only at **step 7** of the queue runner, after steps 4–6 found no held/blocked/delegated
issue to handle. You claim the **oldest eligible** `Agent Todo` issue.

## Eligibility (all three required)

1. Carries the `agent-instructions` label.
2. Title contains `[agent instructions]`.
3. Title's **second bracket** equals **your agent code**.

If any condition fails, the issue is not yours. Do not claim it.

## The claim — three-part write + ledger

Do all four before starting work:

1. **Re-read the issue** (`linear__get_issue`) — the task record may have been edited.
2. **Comment** (`linear__save_comment`): post `AGENT CLAIMED`:
   ```
   AGENT CLAIMED
   Agent: <your-code>
   Run context: Hyperagent thread <thread-id>, model <model>
   Timestamp: <ISO8601>
   Plan: <1–3 sentences>
   ```
3. **Label** (`linear__save_issue`, `labels=["AGENT CLAIMED"]`): append the label.
4. **Status** (`linear__save_issue`, `state="Agent Working"`): patch the status.

Then update your ledger `AGENT STATUS` comment's `Last queue result` to
`claimed <ISSUE-ID>` (in place — never a fresh comment).

## Anti-patterns

- ❌ Claiming without patching status (queue still shows Agent Todo).
- ❌ Claiming an issue whose second bracket isn't your code.
- ❌ Skipping the re-read (the task record may have changed).
- ❌ Posting a fresh AGENT STATUS comment — always edit in place.
