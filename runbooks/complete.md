# Runbook: Complete a Task (AGENT DONE)

> For: all execution runtimes. Triggered at queue-runner step 8.

## Before marking done

Go through every acceptance criterion (task record §4). Each must be verifiably true.
If any is unmet, you are not done — keep working, or go to `block.md` / `fail.md`.

## Choose the target status

- **No human judgment needed** → `AGENT DONE` + status `Agent Done`.
- **Done but needs human review** → `AGENT DONE` + status `Agent Review`.

## The three-part write

1. **Comment** (`linear__save_comment`):
   ```
   AGENT DONE
   Agent: <your-code>
   Run context: Hyperagent thread <thread-id>, model <model>
   Timestamp: <ISO8601>
   Outcome: <2–4 sentences: what was produced/changed>
   Evidence:
     - <link or path>
   Scoped work complete. Ready for review/acceptance per acceptance criteria.
   ```
2. **Label** (`linear__save_issue`, `labels=["AGENT DONE"]`): append.
3. **Status** (`linear__save_issue`, `state="Agent Done"` or `"Agent Review"`): **PATCH.**

Then update your ledger `AGENT STATUS` `Last queue result` to `completed <ISSUE-ID>`
(in place) and `Last successful run` to the current timestamp.

## If the work spawned a follow-on

Note it in the outcome line. The reviewer (Eos) creates the next issue and links this
one in its §3 Sources. Do **not** create the follow-on yourself unless the task
explicitly authorized it.

## Anti-patterns

- ❌ "done" comment without patching status (Paperclip lesson #1).
- ❌ `AGENT DONE` with any acceptance criterion unmet (use BLOCKED/HOLD instead).
- ❌ Omitting evidence — "done" without proof is the failure receipts exist to prevent.
