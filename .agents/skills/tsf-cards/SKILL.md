---
name: tsf-cards
description: Fill pending TSF leaderboard model cards and LTSF paper records from verified public evidence.
---

# TSF cards — Codex project adapter

Read `.claude/skills/tsf-cards/SKILL.md` completely, then follow that canonical
project workflow without mechanically translating its repository paths.

Runtime translation is limited to control surfaces:

- Use Codex tools and subagents instead of source-runtime-specific tool names.
- Do not use external model API credentials; this project skill runs in the active Codex task.
- Preserve the canonical data formats, evidence requirements, verification
  commands, and commit scope defined by the source skill.
