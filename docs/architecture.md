# Open Engine — Architecture (Canonical v2)

> **Status:** Draft v2 — canonical spec, for review by Eos & Dylan.
> **Author:** Bolt (routed by Eos)
> **Date:** 2026-07-04 (v2 rewrite)
> **Source spec:** Nate Jones, canonical Open Engine v2 (full spec via Dylan's paid subscription)

---

## 0. TL;DR

Linear is the shared task queue. Every task is a Linear issue whose **title carries
brackets** (`[agent instructions][<agent-code>][task] …`) and whose **description is a
7-part task record**. Issues carry the `agent-instructions` label. Each runtime executes
an **11-step queue runner** that checks the ledger, does standing preflight, resumes
blocked/held issues, follows up on delegations, and otherwise claims the oldest eligible
`Agent Todo` issue — then **stops after exactly one task**. Every state change is
recorded with a **receipt** (one of 15 canonical tokens) as a comment + label + status
patch. Each agent owns **one `AGENT STATUS` ledger comment** it updates in place every run.

We start with **one task, one agent, one blocker rule, one receipt** and smoke-test
(all 4 canonical tests) before scaling.

---

## 1. Linear Project Setup

### 1.1 Team & project

| Field | Value |
|-------|-------|
| Team | `Motoyuki-dev` · key `MOT` · id `e9848ffc-af19-4bf6-a567-29e9557282a3` |
| Project (new) | `Open Engine` — the coordination substrate, not a product backlog |
| Existing projects (untouched) | GB10 Voice+OCR Pipeline; OB1 / Open Brain Stack Remediation |

### 1.2 The control label

Every Open Engine issue carries the **`agent-instructions`** label. The queue runner's
eligibility check (step 7) requires it — without it, an issue is invisible to the runner.
Created by `scripts/linear/setup.py` (color `#5E6AD2`).

### 1.3 Status workflow

| Open Engine status | Linear type | Meaning |
|--------------------|-------------|---------|
| `Standing` | backlog | Exists but not yet assignable (also used for ledger/directory/standing-skill issues, which never move) |
| `Agent Todo` | unstarted | Eligible to be claimed |
| `Agent Working` | started | Claimed, in progress |
| `Agent Needs Input` | started | Blocked or human-hold |
| `Agent Review` | started | Done, awaiting acceptance |
| `Agent Done` | completed | Accepted |

> ⚠️ **Constraint.** The Linear MCP server exposes `list_issue_statuses` / `get_issue_status`
> but **no status-creation action**. Create the 6 statuses in the Linear UI
> (`Motoyuki-dev → Settings → Workflow → Statuses`) or via Linear's GraphQL API.
> `scripts/linear/setup.py` cannot do it. See §11 Q1.

### 1.4 Receipt labels (14 — one per token except AGENT STATUS)

The 15 receipt tokens each have a label **except `AGENT STATUS`** (which is a single
in-place ledger comment, no label). `scripts/linear/setup.py` creates all 14 idempotently.

| Token | Color | Category |
|-------|-------|----------|
| `AGENT CLAIMED` | `#4EA7FC` blue | task-lifecycle |
| `AGENT DONE` | `#2ECC71` green | task-lifecycle |
| `AGENT BLOCKED` | `#EB5757` red | task-lifecycle |
| `AGENT UNBLOCKED` | `#2ECC71` green | task-lifecycle |
| `AGENT HUMAN HOLD` | `#F5C14B` amber | task-lifecycle |
| `AGENT HUMAN ANSWERED` | `#F5C14B` amber | task-lifecycle |
| `AGENT RESUMED` | `#BB87FC` purple | task-lifecycle |
| `AGENT FAILED` | `#8993A5` grey | task-lifecycle |
| `AGENT APPLIED` | `#00C7B7` teal | standing-context |
| `AGENT SKILL SUBSCRIBED` | `#7C5CFF` indigo | skill |
| `AGENT SKILL INSTALLED` | `#7C5CFF` indigo | skill |
| `AGENT SKILL UPDATED` | `#7C5CFF` indigo | skill |
| `AGENT SKILL DECLINED` | `#8993A5` grey | skill |
| `AGENT FOLLOW-UP` | `#5E6AD2` linear-blue | delegation |
| `AGENT STATUS` | _(no label)_ | ledger |

### 1.5 Standing issues (created by setup)

`scripts/linear/setup.py` creates two standing issues that anchor the engine:

1. **Status ledger** — `[agent instructions][all agents][standing_status] Open Agent Engine status ledger`
2. **Optional skill directory** — `[agent instructions][all agents][optional_standing_skill_directory] Open Engine optional skill directory`

Both stay in `Standing` forever and carry `agent-instructions`. Each agent records their
IDs in its private SKILL.md.

---

## 2. The 7-Part Task Record

Every task issue's **description** is a 7-part record (template: `templates/task-record.md`):

1. **Requester** — who asked (human or agent)
2. **Desired outcome** — what "done" looks like, as an outcome
3. **Sources** — refs, docs, links, prior issue IDs (state that travels)
4. **Acceptance criteria** — testable definition of done (checkboxes)
5. **Boundaries** — what is NOT in scope
6. **Blocker rule** — what to do when stuck (on-Linear → BLOCKED; off-Linear → HOLD)
7. **Receipts** — filled by agents as work progresses

### 2.1 Title format (exact)

```
[agent instructions][<agent-code>][task] <short outcome>
```

The **second bracket** is the runtime that may claim it (enforced by step 7 eligibility).
`[all agents]` is used only for standing/ledger/directory issues, never for tasks.

---

## 3. Receipts (15 canonical tokens)

A receipt is a structured status update. **Every receipt (except STATUS) is a three-part
write:** comment + label + status patch. `scripts/receipts/format.py` formats every token;
`scripts/workflow/transitions.py` maps each to its writes.

### 3.1 The 15 tokens by category

**Task-lifecycle (8):**
- `AGENT CLAIMED` — posted right after moving to Agent Working; the claim lock
- `AGENT DONE` — scoped work finished; pair with `Agent Done` or `Agent Review`
- `AGENT BLOCKED` — answer belongs on the Linear issue; ask **one** question; move to Agent Needs Input
- `AGENT UNBLOCKED` — a blocked issue's answer arrived; posted just before `AGENT RESUMED`
- `AGENT HUMAN HOLD` — answer belongs in the human's own agent thread/app; move to Agent Needs Input
- `AGENT HUMAN ANSWERED` — human answered a hold in their thread; clears the hold
- `AGENT RESUMED` — continuing a paused issue after `UNBLOCKED` or `HUMAN ANSWERED`
- `AGENT FAILED` — unrecoverable failure only; record last safe step and retry count

**Standing-context (1):**
- `AGENT APPLIED` — a runtime installed/adapted a standing context version locally

**Skill (4):**
- `AGENT SKILL SUBSCRIBED` — human approved first install/adaptation of an optional standing skill
- `AGENT SKILL INSTALLED` — runtime actually installed/adapted an optional standing skill
- `AGENT SKILL UPDATED` — a subscribed optional standing skill received a same-scope local update
- `AGENT SKILL DECLINED` — human declined or deferred an optional standing skill

**Delegation (1):**
- `AGENT FOLLOW-UP` — a delegated issue's state changed

**Ledger (1):**
- `AGENT STATUS` — the single ledger comment each agent updates in place (not appended)

> 📝 **Receipt count note (Q for Dylan, §11):** Eos's brief header said "16 receipts" but
> enumerated **15** tokens. This doc implements all 15 faithfully. If a 16th token exists
> in the full canonical spec, send it and I'll add it.

### 3.2 The three-part write, per receipt

| Receipt | Comment body | Label | Status → | Ledger result |
|---------|--------------|-------|----------|---------------|
| `AGENT CLAIMED` | plan | `AGENT CLAIMED` | Agent Working | `claimed ISSUE-ID` |
| `AGENT DONE` (no review) | outcome + evidence | `AGENT DONE` | Agent Done | `completed ISSUE-ID` |
| `AGENT DONE` (needs review) | outcome + evidence | `AGENT DONE` | Agent Review | `completed ISSUE-ID` |
| `AGENT BLOCKED` | one question | `AGENT BLOCKED` | Agent Needs Input | `blocked ISSUE-ID` |
| `AGENT UNBLOCKED` | answer summary | `AGENT UNBLOCKED` | _(none — RESUMED follows)_ | — |
| `AGENT HUMAN HOLD` | need + why | `AGENT HUMAN HOLD` | Agent Needs Input | `holding ISSUE-ID` |
| `AGENT HUMAN ANSWERED` | human answer | `AGENT HUMAN ANSWERED` | _(none — RESUMED follows)_ | — |
| `AGENT RESUMED` | resuming after + what changed | `AGENT RESUMED` | Agent Working | `resumed ISSUE-ID` |
| `AGENT FAILED` | failure + last safe step + retry count | `AGENT FAILED` | Agent Review | `failed ISSUE-ID` |
| `AGENT APPLIED` | context version + local change | `AGENT APPLIED` | _(none)_ | — |
| `AGENT SKILL SUBSCRIBED` | skill@version, scope, approval | `AGENT SKILL SUBSCRIBED` | _(none)_ | — |
| `AGENT SKILL INSTALLED` | skill@version, scope, action | `AGENT SKILL INSTALLED` | _(none)_ | — |
| `AGENT SKILL UPDATED` | skill@version, same-scope | `AGENT SKILL UPDATED` | _(none)_ | — |
| `AGENT SKILL DECLINED` | skill@version, reason | `AGENT SKILL DECLINED` | _(none)_ | — |
| `AGENT FOLLOW-UP` | delegated issue + state change | `AGENT FOLLOW-UP` | _(none)_ | — |
| `AGENT STATUS` | full ledger body | _(no label)_ | _(none — ledger issue stays Standing)_ | _(this IS the ledger)_ |

### 3.3 The run_id question (Paperclip lesson #2)

Open Engine has **no separate activity-log database** — Linear's comment thread *is* the
activity log, and Linear mints its own comment IDs. No FK constraint, no synthetic run_id.
We record a **run context** (Hyperagent thread ID + model) in each receipt for provenance.
If we later add an analytics store, the thread ID is the join key.

---

## 4. The Queue Runner (canonical 11-step process)

This is the exact prompt each runtime executes every run
(`templates/queue-runner-prompt.md`). One run handles **exactly one task issue**.

1. **Open ledger, mark checking.** Identify your agent code; find your `AGENT STATUS`
   comment; update in place — `Last queue result` = `checking`, `Last heartbeat` = now.
2. **Mandatory standing preflight.** Compare local context versions vs standing issues.
   Install/adapt locally **first**, then leave `AGENT APPLIED` only after actually
   installing locally.
3. **Optional standing skill preflight.** Check **only** skills already installed/subscribed.
   Apply same-scope updates automatically (`AGENT SKILL UPDATED`). **Do not browse/install
   unapproved skills** during routine runs.
4. **Check AGENT HUMAN HOLD issues.** If one now shows `AGENT HUMAN ANSWERED`, move to
   Agent Working, leave `AGENT RESUMED`, finish it, **stop**.
5. **Check AGENT BLOCKED issues.** If one now has its answer on the same issue, move to
   Agent Working, leave `AGENT UNBLOCKED` then `AGENT RESUMED`, finish it, **stop**.
6. **Check delegated issues.** Leave `AGENT FOLLOW-UP` on your issue if any delegated
   issue's state changed.
7. **Claim the oldest eligible Agent Todo issue.** Eligible = `agent-instructions` label
   + `[agent instructions]` in title + your agent code as the second title bracket. Move
   to Agent Working, leave `AGENT CLAIMED`, **re-read the issue**.
8. **Do only scoped work.** If done, no human judgment → `AGENT DONE` + `Agent Done`.
   If done but needs review → `AGENT DONE` + `Agent Review`.
9. **If blocked:** answer on Linear → `AGENT BLOCKED` (one question) + `Agent Needs Input`
   + ledger `blocked ISSUE-ID`, stop. Answer in human's thread → `AGENT HUMAN HOLD` +
   `Agent Needs Input` + ledger `holding ISSUE-ID`, stop.
10. **If execution fails unexpectedly** → `AGENT FAILED` with last safe step + retry count.
11. **Update ledger and stop** after exactly one task issue.

### 4.1 Eligibility (step 7), formalized

An issue is eligible for a runtime to claim iff **all three** hold:
- label set includes `agent-instructions`;
- title contains `[agent instructions]`;
- the title's second bracket token equals the runtime's agent code;
- status is `Agent Todo`.

`scripts/workflow/transitions.py::is_eligible_for_claim` encodes this (self-tested).

---

## 5. The Status Ledger

One standing issue: `[agent instructions][all agents][standing_status] Open Agent Engine
status ledger`. Each agent owns **exactly one** top-level `AGENT STATUS` comment, updated
**in place** every run (never a fresh comment). Format (exact):

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

Template: `templates/status-ledger.md`. Runbook: `runbooks/ledger.md`.

---

## 6. Standing Skills Architecture

Optional standing skills are **discoverable from the directory issue but NOT auto-installed**.
- First install requires **human approval in that runtime's agent thread**.
- Approval **subscribes** the runtime to future **same-scope** updates (auto-applied at step 3).
- **Scope expansion needs fresh approval.**

### 6.1 Directory issue

`[agent instructions][all agents][optional_standing_skill_directory] Open Engine optional
skill directory` — a table of available skills (id, version, scope, summary, standing-issue
link). Template: `templates/standing-skill-directory.md`.

### 6.2 Per-skill canonical Standing issue

`[agent instructions][all agents][standing_skill] Install <skill name> <version>` — the
skill's install instructions, version, scope, and what "applied locally" means.

### 6.3 Skill receipts (the 4 tokens)

| Token | When |
|-------|------|
| `AGENT SKILL SUBSCRIBED` | Human approved first install in their thread |
| `AGENT SKILL INSTALLED` | Runtime actually installed/adapted locally |
| `AGENT SKILL UPDATED` | Subscribed skill got a same-scope local update (automatic) |
| `AGENT SKILL DECLINED` | Human declined/deferred |

Runbook: `runbooks/skills.md`.

---

## 7. Private Context (per-runtime SKILL.md)

Each runtime keeps a **local** private context file (not in the repo, not in Linear):
e.g. `~/.hermes/skills/open-engine/SKILL.md` for Eos. It holds: engine version, agent code,
Linear team/project, label, allowed sources, status ledger issue ID, optional skill
directory ID, the runtime's own `AGENT STATUS` comment ID, installed/subscribed skills,
and safety boundaries. Plus a private Standing setup issue listing what to install.

Template: `templates/private-context.md`. For Hyperagent agents (Bolt), the equivalent is
a pinned memory + this repo's docs; the SKILL.md format is the canonical structure.

---

## 8. Naming Conventions (exact)

| Issue type | Title pattern |
|------------|---------------|
| Task | `[agent instructions][<agent-code>][task] <short outcome>` |
| Standing setup | `[agent instructions][all agents][standing_skill] Install Open Engine core context v1` |
| Status ledger | `[agent instructions][all agents][standing_status] Open Engine status ledger` |
| Optional directory | `[agent instructions][all agents][optional_standing_skill_directory] Open Engine optional skill directory` |

Label: `agent-instructions` on **all** of the above.

---

## 9. Agent Integration Pattern

### 9.1 Per-agent roles

| Agent | Code | Role |
|-------|------|------|
| **Eos** | `eos` | Routing / ops — creates tasks, assigns, reviews at Agent Review, owns the backlog. Does not do execution tasks. |
| **Bolt** | `bolt` | Primary builder — claims & completes execution tasks (code, infra, research, deploy) |
| **Zephyr** | `zephyr` | Local builder — claims & completes local-build-flavored execution tasks |

### 9.2 The operating clause (in each runtime's private context / system prompt)

Each runtime's SKILL.md embeds the queue-runner prompt (§4) plus the hard rules:
- One task issue per run.
- Never post a fresh `AGENT STATUS` — edit in place.
- Never claim an issue whose second bracket isn't your code.
- Patch status on every receipt that implies a status change.
- Do not browse/install unapproved skills on routine runs.
- Do not cross the task record's §5 Boundaries.
- Auth by creator, not assignee (Paperclip lesson #3).

### 9.3 Handoffs

A handoff = one agent's `AGENT DONE` becomes another agent's `Agent Todo`. The reviewer
(Eos) creates the follow-on issue, linking the completed one in its §3 Sources. Parent/child
use Linear `parentId` + `blocks`/`blockedBy` **explicitly** — parents close explicitly at
review (Paperclip lesson #4).

### 9.4 Auth boundary (Paperclip lesson #3)

Auth is by **creator, not assignee**. Creators own mutation rights; assignees get
receipt/status writes only. If the task record is wrong, the assignee posts
`AGENT HUMAN HOLD` and the creator amends.

---

## 10. Smoke Tests (4 canonical)

1. **Basic** — claim, done, status, ledger; runner stops after one task. (`examples/smoke-test-1-basic.md`)
2. **Blocked-resume** — intentionally incomplete issue → `AGENT BLOCKED` → answer on issue → `AGENT UNBLOCKED` → `AGENT RESUMED` → `AGENT DONE`. (`examples/smoke-test-2-blocked-resume.md`)
3. **Human-hold** — ask for local permission in agent thread → `AGENT HUMAN HOLD` → `AGENT HUMAN ANSWERED` → completion. (`examples/smoke-test-3-human-hold.md`)
4. **Optional directory** — ask what skills are available → summary without install. (`examples/smoke-test-4-optional-directory.md`)

All four must pass before scaling.

---

## 11. Paperclip Postmortem — Applied

| # | Lesson | How Open Engine v2 satisfies it |
|---|--------|----------------------------------|
| 1 | Agents MUST PATCH issue status on completion | §3: every receipt is a three-part write (comment + label + status). The runner enforces it. |
| 2 | Real run_id­s required (FK constraint) | §3.3: no separate activity-log DB; Linear thread is the log. Run context = provenance, not FK. |
| 3 | Auth boundary is by creator, not assignee | §9.4. |
| 4 | Parents don't auto-close; need explicit blocks links | §9.3: explicit `parentId` + `blocks`/`blockedBy`; parents close at review. |
| 5 | Specs need a Deployment & Operations section | §12. |

---

## 12. Deployment & Operations

### 12.1 What gets deployed

Open Engine is **not a deployed service.** It is:
1. A Linear configuration (project + 6 statuses + `agent-instructions` label + 14 receipt
   labels + 2 standing issues) — created by `scripts/linear/setup.py` (statuses excepted).
2. A GitHub repo (this one) holding spec, templates, runbooks.
3. A private SKILL.md per runtime + the queue-runner prompt embedded in each runtime.

No server, no cron, no database for the engine itself. Linear is the database. The
runtimes are the executor.

### 12.2 Operational procedures

| Need | Do this |
|------|---------|
| Create project + labels + ledger + directory | `python3 scripts/linear/setup.py` (Linear MCP) |
| Create the 6 statuses | Linear UI (Workflow → Statuses) — MCP cannot. §11 Q1. |
| Create a task | Eos fills `templates/task-record.md`, creates via `linear__save_issue` (title brackets, `agent-instructions` label, state Agent Todo) |
| Review blocked/held | Filter Linear: labels `AGENT BLOCKED` / `AGENT HUMAN HOLD` |
| Review completed | Filter: status `Agent Review`, read receipts, accept/return |
| Audit a task | `linear__list_comments` — the thread is the audit log |
| Add a runtime | Create its SKILL.md; embed the queue-runner prompt; ensure Linear + tools; it creates its `AGENT STATUS` comment on first run |

### 12.3 Failure modes

| Failure | Detection | Response |
|---------|-----------|----------|
| "done" comment, no status patch | Status still Agent Working | Reject at review; require three-part write |
| Two runtimes claim same task | Two AGENT CLAIMED comments | Second-bracket eligibility prevents this; if it happens, Eos reassigns |
| Runtime posts fresh STATUS each run | Multiple STATUS comments by same agent | Merge/delete extras; reinstruct to edit in place |
| Task record wrong mid-work | Agent notices | `AGENT HUMAN HOLD`; creator amends; `AGENT RESUMED` |
| Receipt label missing | `linear__save_issue` errors | Re-run `setup.py` (idempotent) |
| Runtime drift (stops patching status) | Quarterly maintenance review | Retire or fix the runtime |

### 12.4 Maintenance

Quarterly, Eos/Dylan: review the last 10 tasks (are the 7 parts right? are receipts left?);
confirm all 14 labels exist and are used; confirm each runtime's SKILL.md + queue-runner
prompt are current; confirm each runtime has exactly one `AGENT STATUS` comment; retire/fix
drifted runtimes.

---

## 13. Open Questions for Eos & Dylan

1. **Status creation in Linear UI** — create the 6 Open Engine statuses (§1.3, ~2 min), or
   run smoke tests on existing statuses and upgrade later? I recommend creating them.
2. **GitHub connection — still pending.** GitHub MCP is available but not OAuth-connected
   on Bolt's account. The repo is fully written and tested locally but cannot be pushed
   until linked. Connect card has been surfaced.
3. **Receipt count: 15 vs 16.** The brief header said "16 receipts" but enumerated 15
   tokens. I implemented all 15. If a 16th canonical token exists in the full spec, send
   it and I'll add it (token, meaning, category, label color).
4. **Single project or per-agent?** I've assumed one `Open Engine` project. Confirm.
5. **Reviewer at Agent Review.** I've assumed Eos. Should Dylan also be a reviewer?
6. **AGENT HUMAN ANSWERED — who posts it?** The canonical spec says the human answers in
   their own thread; the answer then needs to surface on the held Linear issue as
   `AGENT HUMAN ANSWERED`. Is that posted by the human's own agent on their behalf, or by
   the held runtime once it detects the thread answer? I've documented both paths; confirm
   the convention.
