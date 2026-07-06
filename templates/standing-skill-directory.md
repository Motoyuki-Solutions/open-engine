# Optional Standing Skill Directory Template

> One standing issue that lists every optional standing skill available to Open Engine
> runtimes. Skills are discoverable here but **NOT auto-installed**. First install
> requires human approval in that runtime's agent thread; approval subscribes the
> runtime to future same-scope updates. Scope expansion needs fresh approval.
> Source: canonical Open Engine spec (Nate Jones, v2).

---

## The directory issue

| Field | Value |
|-------|-------|
| Title | `[agent instructions][all agents][optional_standing_skill_directory] Open Engine optional skill directory` |
| Team | `Motoyuki-dev` |
| Project | `Open Engine` |
| Status | `Standing` (never moves, never closes) |
| Labels | `agent-instructions` |
| Description | See below |

## Issue description (markdown)

```markdown
# Open Engine — Optional Standing Skill Directory

This is the catalog of optional standing skills available to Open Engine
runtimes. Skills listed here are **discoverable but not auto-installed**.

## How a runtime uses this directory

- On routine runs (queue runner step 3), a runtime checks ONLY skills it has
  already installed/subscribed. It does NOT browse this directory or install
  new skills during a routine run.
- To install a new skill, the runtime leaves `AGENT HUMAN HOLD` on the task
  that needs it, asking the human to approve first install in their agent
  thread. On approval (`AGENT HUMAN ANSWERED`), the runtime leaves
  `AGENT SKILL SUBSCRIBED`, then `AGENT SKILL INSTALLED`.
- Subscription = the runtime gets future **same-scope** updates automatically
  (`AGENT SKILL UPDATED`). A **scope expansion** requires fresh human approval.

## Available optional standing skills

| Skill ID | Version | Scope | Summary | Standing issue |
|----------|---------|-------|---------|----------------|
| _(none yet)_ | | | | |

<!-- To add a skill: create its canonical Standing issue, then add a row here. -->
```

## Per-skill canonical Standing issue

For each optional skill, create a separate Standing issue:

| Field | Value |
|-------|-------|
| Title | `[agent instructions][all agents][standing_skill] Install <skill name> <version>` |
| Status | `Standing` |
| Labels | `agent-instructions` |
| Description | The skill's install instructions, version, scope, and what "applied locally" means for this runtime |

## Skill lifecycle receipts (the 4 skill tokens)

| Token | When | Who posts |
|-------|------|-----------|
| `AGENT SKILL SUBSCRIBED` | Human approved first install/adaptation in their thread | Runtime |
| `AGENT SKILL INSTALLED` | Runtime actually installed/adapted the skill locally | Runtime |
| `AGENT SKILL UPDATED` | A subscribed skill received a same-scope local update | Runtime (automatic) |
| `AGENT SKILL DECLINED` | Human declined or deferred the skill | Runtime (on human's behalf) |

## Directory maintenance

- Adding a skill: create the skill's Standing issue, then add a row to the directory's table.
- Removing/deprecating a skill: leave a note in its row; do not delete the Standing issue
  (subscribed runtimes need to see the deprecation).
- Version bumps that stay in scope: update the Standing issue; subscribed runtimes pick it
  up automatically on their next step-3 preflight.
- Scope expansion: bump the scope field in the Standing issue AND require fresh approval
  from each subscribed runtime (they will re-enter the hold/subscribed flow).
