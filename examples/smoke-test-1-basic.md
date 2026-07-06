# Smoke Test 1 — Basic (claim, done, status, ledger)

> Canonical smoke test. Verifies the minimal happy path: a runtime claims one task,
> completes it, patches status, and updates the ledger — then **stops after one task**.
> Source: canonical Open Engine spec (Nate Jones, v2).

## Setup

- Ledger issue exists (created by `scripts/linear/setup.py`).
- `agent-instructions` label + 14 receipt labels exist.
- The 6 Open Engine statuses exist in Linear (UI step).
- Bolt's private SKILL.md is populated (agent_code=bolt, ledger issue ID, etc.).

## The task issue

- **Title:** `[agent instructions][bolt][task] Add README badge to open-engine repo`
- **Labels:** `agent-instructions`
- **State:** `Agent Todo`
- **§6 Blocker rule:** "If GitHub not connected → AGENT HUMAN HOLD, escalate to Eos, stop."
- **§4 Acceptance criteria:** README in repo has an Open Engine badge; CI badge present.

## Expected run trace (Bolt, one queue-runner pass)

| Step | Action | Receipt / write |
|------|--------|-----------------|
| 1 | Open ledger; set `Last queue result` = `checking`, `Last heartbeat` = now | ledger (in place) |
| 2 | Standing preflight: local engine version matches standing issue | (no AGENT APPLIED — already current) |
| 3 | Optional skill preflight: none installed | (skip) |
| 4 | No `AGENT HUMAN HOLD` issues | (skip) |
| 5 | No `AGENT BLOCKED` issues | (skip) |
| 6 | No delegated issues changed | (skip) |
| 7 | Claim oldest eligible = the badge task | `AGENT CLAIMED` comment + label; state → `Agent Working`; ledger `claimed MOT-xx`; re-read |
| 8 | Do scoped work (edit README, commit, push); no human judgment needed | `AGENT DONE` comment + evidence + label; state → `Agent Done`; ledger `completed MOT-xx` |
| 11 | Update ledger `Last successful run` = now; `Notes` = none | ledger (in place); **STOP** |

## Pass criteria

- [ ] Exactly one task issue was worked (the runner stopped after it).
- [ ] `AGENT CLAIMED` and `AGENT DONE` each appear as a comment **and** a label.
- [ ] Status moved `Agent Todo` → `Agent Working` → `Agent Done` (patched, not just commented).
- [ ] Ledger `AGENT STATUS` comment was **updated in place** (no second comment created).
- [ ] Ledger `Last queue result` ends as `completed MOT-xx`.
- [ ] No external chat transcript was needed to understand the run — the issue's comment
      thread is the full record.
