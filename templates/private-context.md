# Private Context Template (per-runtime SKILL.md)

> Each agent runtime keeps a LOCAL private context file. It is NOT in the repo and NOT
> in Linear — it lives on the runtime's own filesystem. It holds the secrets of
> identity: which agent code this runtime is, where the ledger is, what's allowed.
> Source: canonical Open Engine spec (Nate Jones, v2).

---

## File location

One file per runtime. Examples:

| Runtime | Path |
|---------|------|
| Eos | `~/.hermes/skills/open-engine/SKILL.md` |
| Bolt (Hyperagent) | `~/.hyperagent/skills/open-engine/SKILL.md` (or workspace equivalent) |
| Zephyr | `~/.hermes/skills/open-engine/SKILL.md` (zephyr runtime) |

> For Hyperagent agents (Bolt), the equivalent is a pinned **memory** + this repo's
> docs. The SKILL.md format below is the canonical structure; map it onto whatever
> private-context mechanism the runtime provides.

## File contents (template)

```markdown
# Open Engine — Private Context: <agent-code>

engine_version: open-engine-core-v1
routing_map_version: routing-map-v1
agent_code: <bolt | eos | zephyr>
human_operator: <dylan | …>
runtime: <Claude | Codex | other>

## Linear coordinates
linear_team: Motoyuki-dev        # key MOT, id e9848ffc-af19-4bf6-a567-29e9557282a3
linear_project: Open Engine
agent_instructions_label: agent-instructions

## Standing issue IDs (fill in after setup)
status_ledger_issue_id: <MOT-xx or UUID>      # the standing_status issue
optional_skill_directory_id: <MOT-xx or UUID> # the optional_standing_skill_directory issue
my_status_comment_id: <comment UUID>          # this runtime's AGENT STATUS comment on the ledger

## Allowed sources
# URLs, repos, doc IDs this agent is permitted to read as sources.
- github.com/Motoyuki-Solutions/*
- natesnewsletter.substack.com (canonical spec)
- internal: OB1/Open Brain stack docs

## Installed / subscribed optional skills
# none, or skill-id@version (subscribed) — kept in sync with ledger Optional skills
- none

## Safety boundaries
- Never claim an issue whose second title bracket is not my agent_code.
- Never post a fresh AGENT STATUS comment — edit my existing one in place.
- Never browse/install unapproved optional skills on routine runs (step 3).
- Patch issue status on every receipt that implies a status change.
- One task issue per run. Stop after one.
- Do not cross the task record's §5 Boundaries.
- Auth is by creator, not assignee: I may only mutate issues I created, except
  for receipt/status writes on issues assigned to me.

## Standing setup issue (private)
# A private Standing issue (created by setup, visible to this runtime) listing
# exactly what to install locally to be a compliant Open Engine runtime.
standing_setup_issue_id: <MOT-xx or UUID>
```

## What goes in vs. stays out

| Field | In SKILL.md? | Why |
|-------|--------------|-----|
| agent_code, runtime, operator | ✅ | Identity — who this runtime is |
| Linear team/project/label | ✅ | Coordinates needed every run |
| status_ledger_issue_id, my_status_comment_id | ✅ | Cannot find ledger/comment otherwise |
| optional_skill_directory_id | ✅ | Needed for skill preflight (step 3) |
| Allowed sources | ✅ | Enforces the sources boundary |
| Installed skills | ✅ | Drives step 3 same-scope auto-update |
| Safety boundaries | ✅ | The runtime's hard rules |
| API keys / tokens | ❌ | Never in a file — injected at runtime by the platform |
| Other agents' private context | ❌ | Each runtime sees only its own |
