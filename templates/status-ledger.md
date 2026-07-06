# Status Ledger Template

> One standing issue for the whole engine. Each agent owns exactly ONE top-level
> `AGENT STATUS` comment on it, updated **in place** every run (never fresh comments).
> Source: canonical Open Engine spec (Nate Jones, v2).

---

## The ledger issue

| Field | Value |
|-------|-------|
| Title | `[agent instructions][all agents][standing_status] Open Engine status ledger` |
| Team | `Motoyuki-dev` |
| Project | `Open Engine` |
| Status | `Standing` (backlog — it never moves) |
| Labels | `agent-instructions` |
| Description | See below |

### Issue description (markdown)

```markdown
# Open Engine — Status Ledger

This is the single status ledger for Open Engine. It is a Standing issue: it
never moves out of `Standing` and is never closed.

## How agents use it

Each agent owns EXACTLY ONE top-level `AGENT STATUS` comment on this issue.
On every run, the agent EDITS its existing comment in place — it never posts
a fresh one. The comment is the agent's heartbeat and last-known state.

Do not reply to other agents' STATUS comments. Do not delete them. If an
agent is retired, mark its `Automation state: paused` and leave the comment.

## The AGENT STATUS comment format

AGENT STATUS
Agent: <agent-code>
Human/operator: <name>
Runtime: <Codex | Claude | other>
Automation: <automation name or manual>
Automation state: <installed | manual-required | blocked | paused>
Last heartbeat: <ISO8601 timestamp>
Last queue result: <checking | none | claimed ISSUE-ID | completed ISSUE-ID | blocked ISSUE-ID | holding ISSUE-ID | resumed ISSUE-ID | failed ISSUE-ID>
Last successful run: <ISO8601 timestamp or unknown>
Local context: <engine version>; <routing map version>
Optional skills: <none or skill-id@version subscribed>
Notes: <none or short blocker>
```
```

---

## How an agent creates its STATUS comment (first run only)

1. `linear__list_comments` on the ledger issue.
2. If a top-level comment with body starting `AGENT STATUS` and `Agent: <your-code>`
   already exists → that is yours. Save its comment ID in your private SKILL.md.
3. If not → `linear__save_comment` (create) with the body from `status_ledger()`
   (see `scripts/receipts/format.py`). Save the returned comment ID.

## How an agent updates its STATUS comment (every subsequent run)

- `linear__save_comment` **with the comment `id`** (update in place), never create.
- This is the `comment_inplace` write order in `scripts/workflow/transitions.py`.
- No label is added. No status is patched. The ledger issue stays `Standing`.

## `Last queue result` vocabulary (exact)

| Value | Meaning |
|-------|---------|
| `checking` | Run started, scanning the queue (set in step 1) |
| `none` | Nothing eligible; no task worked this run |
| `claimed ISSUE-ID` | Claimed an Agent Todo issue (step 7) |
| `completed ISSUE-ID` | Finished an issue (step 8) |
| `blocked ISSUE-ID` | Left AGENT BLOCKED, awaiting answer on Linear (step 9) |
| `holding ISSUE-ID` | Left AGENT HUMAN HOLD, awaiting answer in human thread (step 9) |
| `resumed ISSUE-ID` | Resumed a previously blocked/held issue (steps 4/5) |
| `failed ISSUE-ID` | Unrecoverable failure (step 10) |
