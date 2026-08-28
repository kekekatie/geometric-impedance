# GPT workbench

*Branch `gpt/workbench`. A separate, clearly-fenced area, created 2026-08-26 at the request of
Work-GPT (relayed by Katie) and committed by Claude. It branches from the head of the active
science branch `claude/giv-quasicrystal-phason-5syx5s` but is **not** that branch — nothing here
is part of the main experimental record until it passes back through review (see below).*

## What this space is for

- Work-GPT's **independent audit, protocol-design, and exploratory-development** area.
- **Claude acts as the GitHub committer** for changes supplied by Work-GPT, because Work-GPT
  currently has direct **read** access to the repository but not **write** access. Claude holds
  the write-key; Work-GPT retains independent read-and-audit access and reads every resulting
  commit directly.

## Rules of the bench (governance)

1. **No confirmatory experiment may be run from this branch before its pre-registration is
   sealed.** Drafts and designs live here; confirmatory runs wait for a sealed pre-reg.
2. **Proposed scientific changes return to the main experimental line only through an explicit
   review / merge decision** — never by silently flowing from here into the science branch.
3. **Speculative side projects must stay clearly labelled as speculative** and must **not** be
   cited as evidence for GIV or for the main address programme.
4. **Every substantive change names its source** — Work-GPT, Claude, Katie, another crew member,
   or joint — in the commit message and, where useful, in the file itself.

## Roles (as agreed)

- **Current context-rich Claude** — senior historian & primary scientist on
  `claude/giv-quasicrystal-phason-5syx5s`; not to be filled with routine GitHub housekeeping.
- **This workbench's Claude collaborator** — dedicated Work-GPT workbench committer; reads the
  durable record (`CURRENT_SESSION_HANDOFF.md`, `SYNTHESIS.md`, `ROADMAP.md`, `RESULTS_*.md`,
  `PREREG_*.md`) and implements changes Work-GPT specifies, committing them here.
- **Work-GPT** — independent designer / auditor; reads every commit and verifies it.
- **Katie** — occasional short-message relay and final human authority; not the repository porter.

## Orientation for anyone starting here

Read, in order: `CURRENT_SESSION_HANDOFF.md` (full state), `SYNTHESIS.md` (the narrative arc,
Part II is current), `ROADMAP.md` (next checks), then the `substrates/RESULTS_*.md` and
`substrates/PREREG_*.md` for detail. The current front-of-queue design is
`substrates/PREREG_radius_saturation.md` (DRAFT, not sealed).

*Committed by Claude on behalf of Work-GPT. No existing scientific file was altered to create
this workbench.*
