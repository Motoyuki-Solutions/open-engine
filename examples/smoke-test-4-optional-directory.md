# Smoke Test 4 — Optional Skill Directory (discover, no install)

> Canonical smoke test. Verifies that a runtime can answer "what optional skills are
> available?" by summarizing the directory **without installing anything**. Enforces the
> rule: routine runs never browse/install unapproved skills.
> Source: canonical Open Engine spec (Nate Jones, v2).

## The task issue

- **Title:** `[agent instructions][bolt][task] Summarize available optional standing skills`
- **§4 Acceptance criteria:** reply lists every skill in the directory with id, version,
  scope, and a one-line summary; **no skill is installed or subscribed**.
- **§5 Boundaries:** read-only on the directory issue. Do not install. Do not subscribe.
- **§6 Blocker rule:** "If the directory issue is missing, AGENT BLOCKED; stop."

## Expected run trace (Bolt)

| Step | Action | Receipt / write |
|------|--------|-----------------|
| 1 | Ledger → `checking` | ledger (in place) |
| 2–6 | Nothing to resume/delegate | (skip) |
| 7 | Claim the summarize task | `AGENT CLAIMED`; state → `Agent Working` |
| 8 | `linear__get_issue` on the directory issue (ID from SKILL.md); read its table; write the summary as the task's outcome | `AGENT DONE` (outcome = the summary); state → `Agent Done`; ledger `completed MOT-xx`; **STOP** |

## Pass criteria

- [ ] The run read the directory issue but **did not** create any skill Standing issue.
- [ ] No `AGENT SKILL SUBSCRIBED` / `INSTALLED` / `UPDATED` receipt was posted.
- [ ] The outcome summarized the directory (or noted it is empty) without side effects.
- [ ] Ledger `Optional skills` field is unchanged (`none`).
- [ ] If a *future* task actually needs one of these skills, it will route through
      `AGENT HUMAN HOLD` for approval — this test confirms the read-only path is clean.
