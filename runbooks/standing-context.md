# Runbook: Standing Context Preflight (AGENT APPLIED)

> For: all runtimes. Triggered at queue-runner step 2 (mandatory) and step 3 (optional skills).
> Standing context = the engine version + routing map that every runtime must run against.

## Step 2 — Mandatory standing preflight

Every run, **before** touching any task:

1. Read the standing setup issue(s) for Open Engine core context. Current version is in
   your private SKILL.md (`engine_version`, `routing_map_version`).
2. Compare against the version named in the current standing issue.
3. If the standing issue names a **newer** version than you have locally:
   - Install/adapt it locally **first** (update your SKILL.md, your system prompt
     clause, your routing map — whatever "applied locally" means for this runtime).
   - **Only after** the local install succeeds, leave `AGENT APPLIED` on the standing issue:
     ```
     AGENT APPLIED
     Agent: <your-code>
     Run context: <thread-id>, model <model>
     Timestamp: <ISO8601>
     Standing context version: open-engine-core-v<N>
     Installed/adapted locally: <what you changed>
     ```
   - Label: `AGENT APPLIED`. No status change (standing issues stay `Standing`).
4. Update your ledger `Local context` field to the new version.

**Never claim `AGENT APPLIED` for context you have not actually installed locally.**
That is the core integrity rule of the standing layer.

## Step 3 — Optional standing skill preflight

Only for skills already in your ledger's `Optional skills` field (subscribed/installed):

- Check each subscribed skill's Standing issue for a newer **same-scope** version.
- If newer and same scope: apply locally, leave `AGENT SKILL UPDATED` (see `skills.md`).
- **Do NOT browse the optional skill directory or install new skills** during a routine
  run. New skills go through the human-approval path (`block.md` → `AGENT HUMAN HOLD`).
- Scope expansion is **not** a same-scope update — it requires fresh human approval.
