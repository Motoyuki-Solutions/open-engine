# Smoke Test 3 — Human Hold (AGENT HUMAN HOLD → HUMAN ANSWERED → completion)

> Canonical smoke test. Verifies the path where the answer belongs **in the human's
> own agent thread/app**, not on Linear. Typical trigger: a local permission only the
> human can grant. Spans two runner runs.
> Source: canonical Open Engine spec (Nate Jones, v2).

## The task issue

- **Title:** `[agent instructions][bolt][task] Add deploy-to-prod step to CI`
- **§4 Acceptance criteria:** CI workflow has a manual `deploy-prod` job gated on approval.
- **§6 Blocker rule:** "If prod-deploy permission is unclear, AGENT HUMAN HOLD (answer
  belongs in Dylan's thread); stop."

## Run 1 — hits the hold

| Step | Action | Receipt / write |
|------|--------|-----------------|
| 7 | Claim the task | `AGENT CLAIMED`; state → `Agent Working` |
| 8 | Draft the CI change; realize prod-deploy needs Dylan's OK | — |
| 9 | Answer belongs in human's thread → hold | `AGENT HUMAN HOLD` (need: "Approve adding a manual deploy-prod job to CI?"; why: "production deploy permission is your call"); label; state → `Agent Needs Input`; ledger `holding MOT-xx`; **STOP** |

Between runs: Dylan answers in **his** agent thread (e.g. "approved"). That answer is
relayed back onto the held issue as an `AGENT HUMAN ANSWERED` comment (posted by Dylan's
agent on his behalf, or by Bolt's runtime once it sees the thread answer).

## Run 2 — hold cleared, resumes, finishes

| Step | Action | Receipt / write |
|------|--------|-----------------|
| 1 | Ledger → `checking` | ledger (in place) |
| 4 | Detect: issue carries `AGENT HUMAN HOLD` and `AGENT HUMAN ANSWERED` has appeared | — |
| 4 | Move to `Agent Working`; post `AGENT RESUMED` + label | `AGENT RESUMED`; ledger `resumed MOT-xx` |
| 8 | Finish the CI change; commit; needs review (prod-touching) | `AGENT DONE`; state → `Agent Review`; ledger `completed MOT-xx`; **STOP** |

## Pass criteria

- [ ] Run 1 used `AGENT HUMAN HOLD` (not BLOCKED) because the answer belonged off-Linear.
- [ ] The hold receipt named what was needed and why it belongs in the human's thread.
- [ ] Run 2 detected `AGENT HUMAN ANSWERED` and posted `AGENT RESUMED`.
- [ ] Because the work touched prod, it ended in `Agent Review` (not `Agent Done`).
- [ ] No answer was pasted onto the Linear issue as a task comment — the decision stayed
      in the human's thread, as the hold intended.
