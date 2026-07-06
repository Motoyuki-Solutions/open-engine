# scripts/ — Open Engine automation (canonical v2)

These scripts are **spec + helpers**, not a running service. Open Engine has no deployed
runtime (architecture §12.1). The runtimes are the executor; Linear is the database.

## Layout

```
scripts/
├── linear/
│   └── setup.py        # Create project + agent-instructions label + 14 receipt labels + 2 standing issues (idempotent)
├── receipts/
│   └── format.py       # 15 receipt formatters + AGENT STATUS ledger + TOKENS/LABEL_COLORS (tested)
└── workflow/
    └── transitions.py  # Receipt → three-part-write state machine + eligibility check (tested)
```

## How they're used

- `linear/setup.py` — Bolt runs the documented procedure once via `ExecuteIntegration`
  (`linear__save_project`, `linear__create_issue_label`, `linear__save_issue`). Idempotent.
- `receipts/format.py` — `receipt(kind, ...)` builds a comment body; `status_ledger(...)`
  builds the AGENT STATUS ledger body. `TOKENS` and `LABEL_COLORS` are the source of truth
  for the 15 tokens. Self-test: `python3 receipts/format.py`.
- `workflow/transitions.py` — `writes_for_receipt(kind)` returns the label/status/ledger
  result for a receipt; `is_eligible_for_claim(issue, agent_code)` encodes runner step 7.
  Self-test: `python3 workflow/transitions.py`.

## Status creation caveat

`linear/setup.py` does **not** create the 6 Open Engine statuses — the Linear MCP server
exposes no status-creation action. Create them in the Linear UI (Motoyuki-dev → Settings →
Workflow → Statuses) or via Linear's GraphQL API. See `docs/architecture.md` §1.3 & §13 Q1.

## Receipt count

15 canonical tokens. 14 get labels (every token except `AGENT STATUS`, which is a single
in-place ledger comment). `setup.py` creates the 14.
