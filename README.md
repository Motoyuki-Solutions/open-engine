# Open Engine (Canonical v2)

> Multi-agent task management built on Linear. Linear is the shared task queue; agents
> run an 11-step queue runner, claim eligible issues by bracket-coded title, leave
> receipts (15 canonical tokens), and update a single status ledger.

Designed by **Nate Jones** (canonical v2 via Dylan's paid subscription). Adapted for the
Motoyuki-Solutions agent team by Bolt, routed by Eos. Supersedes **Paperclip** (mothballed
2026-06-29).

## The stack we operate

| Layer | Role | Where it lives |
|-------|------|----------------|
| **Open Brain** (memory) | Owned context — what an agent remembers | Hyperagent memories + repo `docs/` |
| **Open Skills** (method) | Repeatable procedures | Hyperagent skills + `runbooks/` |
| **Open Engine** (this repo) | Moves the work — task queue, records, receipts | **Linear** (state of record) |

## What's in this repo

```
open-engine/
├── docs/
│   ├── architecture.md          # Canonical architecture (read first)
│   └── architecture.html        # Published readable version
├── templates/
│   ├── queue-runner-prompt.md   # The exact 11-step runner prompt
│   ├── task-record.md           # 7-part task record + bracket title format
│   ├── status-ledger.md         # The AGENT STATUS ledger issue + format
│   ├── private-context.md       # Per-runtime SKILL.md
│   └── standing-skill-directory.md  # Optional skill directory issue
├── runbooks/
│   ├── claim.md                 # AGENT CLAIMED
│   ├── complete.md              # AGENT DONE
│   ├── block.md                 # AGENT BLOCKED / AGENT HUMAN HOLD
│   ├── resume.md                # AGENT UNBLOCKED / HUMAN ANSWERED / RESUMED
│   ├── fail.md                  # AGENT FAILED
│   ├── ledger.md                # AGENT STATUS (in-place)
│   ├── standing-context.md      # AGENT APPLIED (step 2 preflight)
│   ├── skills.md                # SKILL SUBSCRIBED/INSTALLED/UPDATED/DECLINED
│   └── delegation.md            # AGENT FOLLOW-UP
├── examples/
│   ├── smoke-test-1-basic.md            # claim, done, status, ledger
│   ├── smoke-test-2-blocked-resume.md   # BLOCKED → UNBLOCKED → RESUMED → DONE
│   ├── smoke-test-3-human-hold.md       # HUMAN HOLD → HUMAN ANSWERED → done
│   └── smoke-test-4-optional-directory.md  # discover skills, no install
├── scripts/
│   ├── linear/setup.py          # Create project + label + 14 receipt labels + 2 standing issues
│   ├── receipts/format.py       # 15 receipt formatters + AGENT STATUS ledger (tested)
│   └── workflow/transitions.py  # Receipt → three-part-write state machine (tested)
└── README.md
```

## The 15 canonical receipts

| Category | Tokens |
|----------|--------|
| task-lifecycle | `AGENT CLAIMED`, `AGENT DONE`, `AGENT BLOCKED`, `AGENT UNBLOCKED`, `AGENT HUMAN HOLD`, `AGENT HUMAN ANSWERED`, `AGENT RESUMED`, `AGENT FAILED` |
| standing-context | `AGENT APPLIED` |
| skill | `AGENT SKILL SUBSCRIBED`, `AGENT SKILL INSTALLED`, `AGENT SKILL UPDATED`, `AGENT SKILL DECLINED` |
| delegation | `AGENT FOLLOW-UP` |
| ledger | `AGENT STATUS` (in-place, no label) |

Every receipt (except STATUS) is a **three-part write**: comment + label + status patch.

## Status workflow

`Standing` → `Agent Todo` → `Agent Working` → `Agent Needs Input` → `Agent Review` → `Agent Done`

## Naming conventions (exact)

- Task: `[agent instructions][<agent-code>][task] <short outcome>`
- Standing setup: `[agent instructions][all agents][standing_skill] Install <skill> <v>`
- Status ledger: `[agent instructions][all agents][standing_status] Open Engine status ledger`
- Optional directory: `[agent instructions][all agents][optional_standing_skill_directory] Open Engine optional skill directory`
- Label on all: `agent-instructions`

## Team

| Agent | Code | Role |
|-------|------|------|
| Eos | `eos` | Routing / ops — creates, assigns, reviews |
| Bolt | `bolt` | Primary builder |
| Zephyr | `zephyr` | Local builder |

## Quick start

1. **Create the 6 statuses in Linear UI** (Motoyuki-dev → Workflow → Statuses). The MCP can't.
2. `python3 scripts/linear/setup.py` — creates project, `agent-instructions` label, 14 receipt
   labels, the ledger standing issue, and the optional-skill-directory standing issue.
3. Each runtime creates its private SKILL.md (`templates/private-context.md`) and embeds the
   [queue-runner prompt](templates/queue-runner-prompt.md).
4. Run the [4 smoke tests](examples/) before scaling.

Full detail: [`docs/architecture.md`](docs/architecture.md).

## Provenance

- Original design: Nate Jones, canonical Open Engine v2 (full spec via Dylan's paid subscription).
- Public framing: "Make Your AI Agents Hand Off Work Without You" (Jun 26, 2026),
  `natesnewsletter.substack.com/p/ai-agent-handoffs`.
- Supersedes Paperclip (mothballed 2026-06-29). All 5 Paperclip postmortem lessons applied
  (see `docs/architecture.md` §11).
