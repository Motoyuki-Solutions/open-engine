#!/usr/bin/env python3
"""
Open Engine — Linear setup (canonical v2).

Creates (idempotently), in order:
  1. The "Open Engine" project in the Motoyuki-dev team.
  2. The `agent-instructions` label (required for issue eligibility).
  3. The 15 receipt labels (one per canonical receipt token that has a label;
     AGENT STATUS has none).
  4. The status ledger standing issue.
  5. The optional skill directory standing issue.

Status creation (the 6 Open Engine statuses) is NOT done here — the Linear MCP
server exposes no status-creation action. Create them in the Linear UI
(Workflow → Statuses) or via Linear's GraphQL API. See docs/architecture.md §1.3.

This script is a SPEC for the setup procedure. The actual writes go through the
Linear MCP integration, which Bolt invokes via ExecuteIntegration. This file
documents the exact calls and arguments so the procedure is reproducible.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from receipts.format import TOKENS, LABEL_COLORS, LABEL_NAMES  # noqa: E402

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

TEAM_ID = "e9848ffc-af19-4bf6-a567-29e9557282a3"  # Motoyuki-dev
TEAM_KEY = "MOT"

PROJECT = {
    "name": "Open Engine",
    "team": TEAM_ID,
    "description": (
        "Multi-agent task queue built on Linear. Agents read assigned issues, "
        "move statuses, leave receipts, and use issue history for coordination. "
        "Canonical spec: Nate Jones, v2. See repo: "
        "github.com/Motoyuki-Solutions/open-engine"
    ),
}

# The one label every Open Engine issue must carry (eligibility gate).
AGENT_INSTRUCTIONS_LABEL = {
    "name": "agent-instructions",
    "color": "#5E6AD2",  # Linear blue
    "description": "Open Engine control label. Required for queue-runner eligibility.",
}

# 15 receipt labels, one per token. The Linear label NAME is lowercase
# kebab-case (LABEL_NAMES); the receipt *comment body* stays uppercase (TOKENS).
# agent-status IS a real label (Eos confirmed). agent-instructions is separate
# (the control label) and is created in its own step.
RECEIPT_LABELS = [
    {"name": LABEL_NAMES[tok], "color": LABEL_COLORS[tok], "description": TOKENS[tok]}
    for tok in TOKENS
]

# The two standing issues that anchor the engine.
LEDGER_ISSUE = {
    "title": "[agent instructions][all agents][standing_status] Open Agent Engine status ledger",
    "team": TEAM_ID,
    "project": "Open Engine",
    "state": "Standing",
    "labels": ["agent-instructions"],
    "description": (  # see templates/status-ledger.md for the full body
        "# Open Engine — Status Ledger\n\n"
        "Standing issue. Each agent owns exactly ONE top-level AGENT STATUS "
        "comment, updated in place every run. See templates/status-ledger.md."
    ),
}

DIRECTORY_ISSUE = {
    "title": ("[agent instructions][all agents][optional_standing_skill_directory] "
              "Open Engine optional skill directory"),
    "team": TEAM_ID,
    "project": "Open Engine",
    "state": "Standing",
    "labels": ["agent-instructions"],
    "description": (  # see templates/standing-skill-directory.md for the full body
        "# Open Engine — Optional Standing Skill Directory\n\n"
        "Catalog of optional standing skills. Discoverable, NOT auto-installed. "
        "First install needs human approval in the runtime's agent thread. "
        "See templates/standing-skill-directory.md."
    ),
}


# ----------------------------------------------------------------------------
# Procedure (executed by Bolt through the Linear MCP integration)
# ----------------------------------------------------------------------------
#
# STEP 0 — Preflight: confirm the team exists.
#   linear__list_teams  -> expect Motoyuki-dev (id TEAM_ID).
#
# STEP 1 — Create / find the project.
#   linear__list_projects  -> look for name == "Open Engine"
#   If missing:
#     linear__save_project({ name, team=TEAM_ID, description })
#   Record project id.
#
# STEP 2 — Ensure the agent-instructions label exists.
#   linear__list_issue_labels  -> look for "agent-instructions"
#   If missing:
#     linear__create_issue_label({ name, color, description, team=TEAM_ID })
#
# STEP 3 — Ensure all 15 receipt labels exist.
#   linear__list_issue_labels  -> set of existing names
#   For each label in RECEIPT_LABELS not already present:
#     linear__create_issue_label({ name, color, description, team=TEAM_ID })
#
# STEP 4 — Create the status ledger standing issue (if missing).
#   linear__list_issues(project="Open Engine", labels=["agent-instructions"])
#     -> look for title == LEDGER_ISSUE["title"]
#   If missing:
#     linear__save_issue({
#       title, team=TEAM_ID, project="Open Engine", state="Standing",
#       labels=["agent-instructions"], description=<full body from template>,
#     })
#   Record ledger issue id. Each agent stores this in its private SKILL.md.
#
# STEP 5 — Create the optional skill directory standing issue (if missing).
#   Same pattern as step 4 but with DIRECTORY_ISSUE.
#   Record directory issue id.
#
# STEP 6 — Report.
#   Print: project URL, labels created vs. already-present, ledger issue URL,
#   directory issue URL. Remind that the 6 statuses must be created in the UI.
#
# NOTE on statuses: the 6 Open Engine statuses (Standing, Agent Todo,
# Agent Working, Agent Needs Input, Agent Review, Agent Done) are NOT created
# here. Create them in Linear UI:
#   Motoyuki-dev -> Settings -> Workflow -> Statuses & labels
# See docs/architecture.md §1.3.

if __name__ == "__main__":
    print("Open Engine Linear setup — canonical v2")
    print(f"Team: {TEAM_KEY} ({TEAM_ID})")
    print(f"Project: {PROJECT['name']}")
    print(f"Required control label: {AGENT_INSTRUCTIONS_LABEL['name']}")
    print(f"Receipt labels to ensure: {len(RECEIPT_LABELS)} "
          f"(of {len(TOKENS)} tokens; agent-status IS a label)")
    for lbl in RECEIPT_LABELS:
        print(f"  - {lbl['name']:<26} {lbl['color']}")
    print(f"\nStanding issues to create:")
    print(f"  1. {LEDGER_ISSUE['title']}")
    print(f"  2. {DIRECTORY_ISSUE['title']}")
    print("\nNOTE: the 6 Open Engine statuses must be created in the Linear UI "
          "(Workflow → Statuses). The MCP server cannot create statuses.")
