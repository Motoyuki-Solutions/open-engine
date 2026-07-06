# Open Engine — Deployment Guide

> How each agent in Dylan's team connects to the Open Engine queue, finds its private context, and runs the queue runner. Clear enough that a new agent can onboard from this guide alone.
>
> **Canonical reference:** `docs/architecture.md` (full architecture), `templates/queue-runner-prompt.md` (the exact 11-step runner), `templates/private-context.md` (SKILL.md template). This guide is the *onboarding* companion to those.

---

## 0. What Open Engine is, in one paragraph

Linear is the shared task queue. Each agent runs an **11-step queue runner** on every activation: it checks the status ledger, does standing-context preflight, resumes any blocked/held issues, follows up on delegations, and otherwise **claims the oldest eligible `Agent Todo` issue whose second title bracket matches the agent's code** — then does the scoped work, leaves a receipt, patches the issue status, updates the ledger, and **stops after exactly one task**. No server, no cron, no database: Linear is the database, the agents are the runtime.

---

## 1. The team

| Agent | Code | Runtime / host | Lane (what it does) | Private context path |
|-------|------|-----------------|---------------------|----------------------|
| **Eos** | `eos` | Hermes (default profile) | Ops, routing, review, proxy — creates tasks, assigns, reviews at `Agent Review`, owns the backlog. **Does not do execution tasks.** | `~/.hermes/skills/open-engine/SKILL.md` |
| **Zephyr** | `zephyr` | Hermes (host profile `~/.hermes/profiles/zephyr/`) | Deep builder — local infra: GB10 cluster, NFS, Docker, voice/OCR pipeline | `~/.hermes/profiles/zephyr/skills/open-engine/SKILL.md` |
| **Bolt** | `bolt` | Hyperagent (hosted) | Primary builder — Open Engine, GitHub PRs, Google Workspace, research, deploy | Hyperagent pinned memory + this repo's `docs/` (the SKILL.md format is the canonical structure; map it onto the runtime's private-context mechanism) |

> **Why two runtimes.** Eos and Zephyr run on **Hermes** (a local agent host with per-profile skill directories at `~/.hermes/...`). Bolt runs on **Hyperagent** (a hosted agent platform whose private-context equivalent is a pinned memory plus the repo's docs). The Open Engine spec is runtime-neutral: the SKILL.md format is the same; only *where it lives* differs. The canonical `~/.hermes/skills/open-engine/SKILL.md` path in the spec is the Hermes convention; Bolt uses the Hyperagent equivalent.

---

## 2. Standing anchors (workspace-wide, same for every agent)

Every agent needs to know these three Linear issues by ID. They are created once during setup and referenced from each private context file.

| Anchor | Issue ID | Title | Purpose |
|--------|----------|-------|---------|
| Status ledger | **MOT-40** | `[agent instructions][all agents][standing_status] Open Agent Engine status ledger` | Each agent owns exactly one top-level `AGENT STATUS` comment here, updated in place every run |
| Optional skill directory | **MOT-41** | `[agent instructions][all agents][optional_standing_skill_directory] Open Engine optional skill directory` | Catalog of optional standing skills (discoverable, not auto-installed) |
| Core context setup | **MOT-42** | `[agent instructions][all agents][standing_skill] Install Open Engine core context v1` | What every runtime must install locally before its first run |

Linear project: **Open Engine** (`linear.app/motoyukidev/project/open-engine-20edfd0a9b06`).
Linear team: **Motoyuki-dev** (key `MOT`).
Control label: **`agent-instructions`** — required on every Open Engine issue (the eligibility gate).

---

## 3. Per-agent setup

### 3.1 Private context file (SKILL.md)

Each runtime keeps a **local** private context file holding the secrets of identity: which agent code this runtime is, where the ledger is, what's allowed. **It is not in the repo and not in Linear** — it lives on the runtime's own filesystem. Template: `templates/private-context.md`.

**Eos** — `~/.hermes/skills/open-engine/SKILL.md`
**Zephyr** — `~/.hermes/profiles/zephyr/skills/open-engine/SKILL.md`
**Bolt** — Hyperagent pinned memory (key: `open-engine-private-context`) + this repo's `docs/`. The fields below are the canonical structure; Bolt maps them onto the pinned-memory mechanism.

The file must contain:

```markdown
# Open Engine — Private Context: <agent-code>

engine_version: open-engine-core-v1
routing_map_version: routing-map-v1
agent_code: <eos | zephyr | bolt>
human_operator: dylan
runtime: <Hermes | Hyperagent | other>

## Linear coordinates
linear_team: Motoyuki-dev
linear_project: Open Engine
agent_instructions_label: agent-instructions

## Standing issue IDs
status_ledger_issue_id: MOT-40
optional_skill_directory_id: MOT-41
my_status_comment_id: <filled on first run, after you create your AGENT STATUS comment on MOT-40>

## Allowed sources
- github.com/Motoyuki-Solutions/*
- natesnewsletter.substack.com (canonical spec)
- internal: OB1/Open Brain stack docs, GB10 cluster docs

## Installed / subscribed optional skills
- none

## Safety boundaries
- One task issue per run. Stop after one.
- Never post a fresh AGENT STATUS comment — edit your existing one in place.
- Never claim an issue whose second title bracket is not your agent_code.
- Patch issue status on every receipt that implies a status change.
- Do not browse or install unapproved optional skills on routine runs.
- Do not cross the task record's §5 Boundaries.
- Auth is by creator, not assignee: mutate only issues you created, except for
  receipt/status writes on issues assigned to you.
```

### 3.2 The queue runner prompt

Each runtime embeds the 11-step queue runner prompt (see `templates/queue-runner-prompt.md`) into its system prompt / skill instructions. The runner is the same for all three agents — the only per-agent difference is the `agent_code` used at step 7's eligibility check and step 1's ledger comment.

**Where it goes:**
- **Eos / Zephyr (Hermes):** the runner prompt is the body of the `open-engine` skill at `~/.hermes/skills/open-engine/` (Eos) or `~/.hermes/profiles/zephyr/skills/open-engine/` (Zephyr). Hermes loads the skill's instructions when the agent activates.
- **Bolt (Hyperagent):** the runner prompt is part of Bolt's agent system prompt (the "Open Engine operating clause"). The Hyperagent platform injects it on each run.

The full 11 steps are in `templates/queue-runner-prompt.md`. Summary: (1) open ledger, mark `checking`; (2) mandatory standing preflight; (3) optional skill preflight; (4) check human-hold issues; (5) check blocked issues; (6) check delegations; (7) claim the oldest eligible Agent Todo issue; (8) do scoped work, AGENT DONE; (9) if blocked, AGENT BLOCKED or AGENT HUMAN HOLD; (10) if failed, AGENT FAILED; (11) update ledger, stop after one task.

---

## 4. Verify the connection (Linear MCP test)

Before the first real run, confirm the runtime can reach Linear through the MCP integration. Run this from the runtime and expect a non-empty team list:

**Hermes (Eos/Zephyr):** invoke the Linear MCP `list_teams` tool from the agent's skill context. Expected: a team named `Motoyuki-dev` (key `MOT`).

**Hyperagent (Bolt):** the agent calls `linear__list_teams` via the integration. Expected: `Motoyuki-dev`.

Then confirm the three anchors are reachable:

```
linear__get_issue(id: "MOT-40")   # status ledger
linear__get_issue(id: "MOT-41")   # optional skill directory
linear__get_issue(id: "MOT-42")   # core context setup
```

All three should return with `status: "Standing"` and the `agent-instructions` label. If any returns empty or errors, the Linear MCP connection is not ready — fix before proceeding.

Also confirm the receipt labels exist (created during setup, but verify):

```
linear__list_issue_labels(team: "Motoyuki-dev")
```

Expected: `agent-instructions` plus the 15 kebab-case receipt labels (`agent-claimed`, `agent-done`, `agent-blocked`, `agent-unblocked`, `agent-human-hold`, `agent-human-answered`, `agent-resumed`, `agent-failed`, `agent-applied`, `agent-skill-subscribed`, `agent-skill-installed`, `agent-skill-updated`, `agent-skill-declined`, `agent-follow-up`, `agent-status`).

---

## 5. First-run checklist (onboarding a new agent)

Use this checklist every time a new runtime joins Open Engine. Complete in order.

- [ ] **1. Confirm Linear MCP is connected** and the runtime can call `linear__list_teams` (expect `Motoyuki-dev`). See §4.
- [ ] **2. Confirm the 6 Open Engine statuses exist** in Linear (`Standing`, `Agent Todo`, `Agent Working`, `Agent Needs Input`, `Agent Review`, `Agent Done`). These are created in the Linear UI (Workflow → Statuses) — the MCP cannot create them. If missing, an org admin creates them.
- [ ] **3. Confirm the 16 labels exist** (`agent-instructions` + 15 kebab receipt labels). See §4. If any are missing, create them with `linear__create_issue_label`.
- [ ] **4. Confirm the 3 standing anchors exist** (MOT-40, MOT-41, MOT-42) and are `Standing`. See §2.
- [ ] **5. Create the private context file** (SKILL.md) for this runtime, filling `agent_code`, `runtime`, `human_operator`, the standing issue IDs, allowed sources, and safety boundaries. See §3.1. Leave `my_status_comment_id` blank for now.
- [ ] **6. Embed the queue runner prompt** into the runtime's system prompt / skill. See §3.2.
- [ ] **7. Do the mandatory standing preflight (runner step 2):** read MOT-42 (core context v1), install/adapt it locally (update your SKILL.md `engine_version`/`routing_map_version` to match), and leave `AGENT APPLIED` on MOT-42 **only after installing locally**.
- [ ] **8. Create your AGENT STATUS comment on MOT-40** (runner step 1, first run): `linear__list_comments` on MOT-40; if no comment with body starting `AGENT STATUS` and `Agent: <your-code>` exists, `linear__save_comment` to create one with `Last queue result: checking`. Save the returned comment ID into your SKILL.md as `my_status_comment_id`.
- [ ] **9. Run smoke test 1 (basic)** — see §6. Must pass before the agent takes real tasks.
- [ ] **10. Run smoke tests 2, 3, 4** before the agent is considered production-ready.

---

## 6. The 4 smoke tests — what they verify and when to run them

Run all four before an agent takes real tasks. Each is documented with a step-by-step trace and pass criteria in `examples/`.

| # | Test | What it verifies | File |
|---|------|------------------|------|
| 1 | **Basic** | The minimal happy path: claim, done, status patched, ledger updated, runner stops after exactly one task. | `examples/smoke-test-1-basic.md` |
| 2 | **Blocked-resume** | The blocked-then-resumed path where the answer belongs on Linear: AGENT BLOCKED → answer on issue → AGENT UNBLOCKED → AGENT RESUMED → AGENT DONE. Spans two runs. | `examples/smoke-test-2-blocked-resume.md` |
| 3 | **Human-hold** | The path where the answer belongs in the human's own agent thread (a permission/decision): AGENT HUMAN HOLD → AGENT HUMAN ANSWERED → completion. Spans two runs. | `examples/smoke-test-3-human-hold.md` |
| 4 | **Optional directory** | The runtime can answer "what optional skills are available?" by summarizing the directory **without installing anything** — enforcing the no-auto-install rule. | `examples/smoke-test-4-optional-directory.md` |

**When to run them:**
- **Onboarding a new runtime** → all 4, in order, before real tasks.
- **After any change to the queue runner prompt, the receipt vocabulary, or the Linear setup** → re-run test 1 (and the one relevant to the change).
- **Quarterly maintenance** → re-run all 4 to catch drift (an agent that stops patching status will fail test 1).

**How to set up a smoke test:** Eos creates the test task issue (with the correct `[<agent-code>]` bracket for the runtime under test) in the Open Engine project, status `Agent Todo`, label `agent-instructions`. The runtime then runs the queue runner against it. Each test's file specifies the exact issue to create and the expected receipt/status trace.

---

## 7. Issue naming convention (exact)

Every Open Engine issue's title uses bracket prefixes. The `agent-instructions` label is also required on every issue (the eligibility gate for step 7).

| Issue type | Title pattern | Who can claim |
|------------|---------------|---------------|
| Task | `[agent instructions][<agent-code>][task] <short outcome>` | Only the runtime whose code matches the **second bracket** |
| Standing setup | `[agent instructions][all agents][standing_skill] Install <skill> <version>` | n/a (Standing, never claimed) |
| Status ledger | `[agent instructions][all agents][standing_status] Open Engine status ledger` | n/a (Standing, never claimed) |
| Optional directory | `[agent instructions][all agents][optional_standing_skill_directory] Open Engine optional skill directory` | n/a (Standing, never claimed) |

**Examples:**
- `[agent instructions][bolt][task] Write Open Engine deployment guide for the team`
- `[agent instructions][zephyr][task] Reconfigure GB10 NFS mount`
- `[agent instructions][eos][task] Triage Agent Review queue`

`[all agents]` is used only for the three standing issue types, never for tasks. A task with `[all agents]` as the second bracket would be claimable by no specific runtime and should not be created — assign a concrete agent code.

---

## 8. Day-to-day operation

Once onboarded, an agent's activation is always the same: run the queue runner (§3.2). One run = one task. The runner handles ledger, preflight, resumes, delegations, and claiming in that order; the agent does the scoped work and leaves the matching receipt.

**For Eos specifically** — Eos does not run the queue runner to claim execution tasks (Eos doesn't do execution). Eos's loop is: create tasks with the right brackets, assign them, watch the `Agent Review` queue, accept or return, and triage `agent-blocked`/`agent-human-hold` issues. Eos still maintains an AGENT STATUS comment on MOT-40 (as the routing runtime) and may use AGENT FOLLOW-UP to note delegation state changes.

**Receipts cheat-sheet** (15 tokens; the comment body is uppercase, the Linear label is kebab-case):

- Task lifecycle: `AGENT CLAIMED`, `AGENT DONE`, `AGENT BLOCKED`, `AGENT UNBLOCKED`, `AGENT HUMAN HOLD`, `AGENT HUMAN ANSWERED`, `AGENT RESUMED`, `AGENT FAILED`
- Standing context: `AGENT APPLIED`
- Skills: `AGENT SKILL SUBSCRIBED`, `AGENT SKILL INSTALLED`, `AGENT SKILL UPDATED`, `AGENT SKILL DECLINED`
- Delegation: `AGENT FOLLOW-UP`
- Ledger: `AGENT STATUS` (single in-place comment, label `agent-status`)

Every receipt except STATUS is a **three-part write**: comment + label + status patch. See `docs/architecture.md` §3.2 for the full per-receipt table.

---

## 9. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Runner finds no eligible issue | Issue missing `agent-instructions` label, or second bracket ≠ your code, or status ≠ `Agent Todo` | Fix the issue's label/title/status (Eos amends) |
| `linear__save_issue` errors on a label | That kebab label doesn't exist yet | Create it with `linear__create_issue_label`, or re-run `scripts/linear/setup.py` (idempotent) |
| Two AGENT STATUS comments by the same agent on MOT-40 | The runtime posted a fresh comment instead of editing in place | Merge/delete the extra; update your SKILL.md `my_status_comment_id` to the one you keep; always edit by comment `id` going forward |
| Status shows "Agent Working" but work is done | Agent left a "done" comment without patching status (Paperclip lesson #1) | Reject at review; the agent must complete the three-part write |
| An issue is stuck in `Agent Needs Input` | No one answered the AGENT BLOCKED question / AGENT HUMAN HOLD | Reviewer (Eos) answers on the issue (BLOCKED) or in their thread (HOLD); the owning runtime resumes on its next run |
| A runtime's AGENT STATUS `Last heartbeat` is stale | The runtime hasn't run in a while / is down | Investigate; if retired, set its `Automation state: paused` and leave the comment |

---

## 10. Provenance & boundaries of this guide

- This guide is the **onboarding companion** to `docs/architecture.md`. The architecture doc is the source of truth for the full spec; this guide focuses on *how to stand up and join*.
- It does not modify the architecture, templates, or scripts — it references them.
- Canonical spec: Nate Jones, Open Engine v2. Public framing: "Make Your AI Agents Hand Off Work Without You" (Jun 26, 2026), `natesnewsletter.substack.com/p/ai-agent-handoffs`.
- Team roster and private-context paths sourced from the MOT-44 task record §3.
