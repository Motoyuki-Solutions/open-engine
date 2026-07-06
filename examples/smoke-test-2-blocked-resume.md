# Smoke Test 2 — Blocked → Resume (AGENT BLOCKED → UNBLOCKED → RESUMED → DONE)

> Canonical smoke test. Verifies the blocked-then-resumed path where the answer
> belongs **on the Linear issue**. Spans two runner runs.
> Source: canonical Open Engine spec (Nate Jones, v2).

## The task issue

- **Title:** `[agent instructions][bolt][task] Wire OB1 review endpoint into dashboard`
- **§4 Acceptance criteria:** dashboard calls `ob1_review_memory` and renders the queue.
- **§6 Blocker rule:** "If the endpoint URL/contract is unclear, AGENT BLOCKED with the
  one question on this issue; stop."
- Deliberately **incomplete** at creation: the §3 Sources do not specify the endpoint URL.

## Run 1 — gets blocked

| Step | Action | Receipt / write |
|------|--------|-----------------|
| 7 | Claim the task | `AGENT CLAIMED`; state → `Agent Working` |
| 8 | Start work; discover §3 lacks the endpoint URL | — |
| 9 | Answer belongs on Linear → ask **one** question | `AGENT BLOCKED` (one question: "What is the ob1_review_memory URL and request shape?"); label; state → `Agent Needs Input`; ledger `blocked MOT-xx`; **STOP** |

Between runs: Eos (or Dylan) adds the answer as a **comment on the same issue**.

## Run 2 — detects answer, resumes, finishes

| Step | Action | Receipt / write |
|------|--------|-----------------|
| 1 | Ledger → `checking` | ledger (in place) |
| 5 | Detect: issue carries `AGENT BLOCKED` and now has an answer comment | — |
| 5 | Move to `Agent Working`; post `AGENT UNBLOCKED` (answer summary) + label | `AGENT UNBLOCKED`; ledger unchanged yet |
| 5 | Post `AGENT RESUMED` + label; state already `Agent Working` | `AGENT RESUMED`; ledger `resumed MOT-xx` |
| 8 | Finish the wiring; no human judgment needed | `AGENT DONE` + evidence; state → `Agent Done`; ledger `completed MOT-xx`; **STOP** |

## Pass criteria

- [ ] Run 1 left exactly one `AGENT BLOCKED` with exactly one question.
- [ ] Run 2 posted `AGENT UNBLOCKED` **then** `AGENT RESUMED` (both, in that order).
- [ ] Status path: `Agent Todo` → `Agent Working` → `Agent Needs Input` → `Agent Working` → `Agent Done`.
- [ ] The answer was read from the issue's own comments (not from an external chat).
- [ ] Each run handled one issue and stopped.
