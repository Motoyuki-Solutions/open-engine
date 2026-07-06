# Runbook: Delegation Follow-Up (AGENT FOLLOW-UP)

> For: all runtimes. Triggered at queue-runner step 6.
> When you have delegated an issue to another agent, check whether its state changed.

## Step 6 — Check delegated issues

1. Identify issues you created that you delegated to another agent (you are the
   creator; the second title bracket is another agent's code; or `assignee` is another
   runtime).
2. For each, check whether its state changed since your last run (e.g. it moved to
   `Agent Done`, `Agent Review`, or `Agent Needs Input`).
3. If any changed, leave `AGENT FOLLOW-UP` on **your** (delegating) issue:
   ```
   AGENT FOLLOW-UP
   Agent: <your-code>
   Run context: <thread-id>, model <model>
   Timestamp: <ISO8601>
   Delegated issue: <MOT-xx>
   State change: <e.g. moved to Agent Done by zephyr>
   ```
   - Label: `AGENT FOLLOW-UP`. No status change to your issue (unless the change
     unblocks your own work — then handle per `resume.md`).

## When delegation unblocks your own work

If a delegated issue moving to `Agent Done` means your own blocked issue now has its
answer on Linear, treat it as a step-5 resume: `AGENT UNBLOCKED` → `AGENT RESUMED` →
finish → stop. The delegation follow-up is noted, but the resume counts as your one
task issue for the run.

## Anti-patterns

- ❌ Posting AGENT FOLLOW-UP on the delegated issue (post on YOUR issue).
- ❌ Stopping after a mere state-change note unless it unblocks your work — step 6 is
  bookkeeping; continue to step 7 if nothing else applied.
