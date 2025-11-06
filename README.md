# RAW SKILLS

A large, ready-to-use collection of **agent skills** (`SKILL.md` instruction packs) that
work with any AI coding agent - Trayambak, Claude Code, OpenCode, Codex CLI, Gemini CLI, Cursor,
Windsurf, GitHub Copilot, Cline, Roo Code, Aider, Continue, Zed and plain chat models.

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Files](https://img.shields.io/badge/files-13%2C309-blue.svg)](#whats-inside)
[![Folders](https://img.shields.io/badge/folders-5%2C009-blue.svg)](#whats-inside)
[![Last Updated](https://img.shields.io/badge/last%20updated-2026--11--05-lightgrey.svg)](#)


- Last updated: **2026-11-05**
- Skill index: [SKILLS.md](SKILLS.md) - all 1,962 top-level skill folders with descriptions

---

## What's inside

| Metric | Value |
| --- | --- |
| Files | 13,309 |
| Folders | 5,009 |
| Top-level skill folders | 1,962 (1,958 ship a `SKILL.md`; the rest are bundles) |
| Total size | ~172 MB |

Every top-level folder is one skill. The contents are not uniform - some skills are a
single file, others ship scripts, references, templates and assets:

```
<skill-name>/
  SKILL.md          # required - frontmatter (name, description) + instructions
  scripts/          # optional - helper scripts, CLIs, generators
  references/       # optional - deep-dive docs loaded on demand
  examples/         # optional - sample inputs and outputs
  assets/           # optional - images, fonts, templates
```

Only `SKILL.md` matters for discovery. The rest is progressive disclosure - the agent
reads it only when the skill says so.

A few folders are bundles rather than single skills: `security/` (AWS security skills),
`libreoffice/` (writer, calc, impress, draw, base), `linear/` (a plugin manifest) and
`SPDD/` (a staged spec-driven workflow). Everything else is a standalone skill folder.

---

## Install

```bash
git clone https://github.com/SHRIJANAGAIN/RAW-SKILLS.git
```

Copy the skills you want into your agent's skill directory (see the table below).
Copy only what you need - loading 1,963 skills at once floods the model's context.

`scripts/install-skills.ps1` and `scripts/install-skills.sh` are included for bulk
copying (pick specific skills or a whole category).

---

## Use with any AI agent

Most agents now read the Agent Skills convention: one folder per skill, with a
`SKILL.md` whose frontmatter contains `name` and `description`. If your tool supports
`.agents/skills/`, that single path works for several agents at once.

| Agent | Where to put skills | How to invoke |
| --- | --- | --- |
| Trayambak | `<project>/skills/<name>/SKILL.md`<br>`<project>/.trayambak/skills/<name>/SKILL.md`<br>`~/.trayambak/skills/<name>/SKILL.md`<br>*(ya `skillsDir` config / `TRAYAMBAK_SKILLS_DIR` se koi bhi dir)* | `skill__<name>` tool (model khud call karta hai); prompt me skill ka naam likhne par preload; restart TUI zaroori |
| Universal / Agent Skills standard | `.agents/skills/<name>/SKILL.md` (project) or `~/.agents/skills/<name>/SKILL.md` (global) | Agent loads it on demand |
| Claude Code | `.claude/skills/<name>/SKILL.md` or `~/.claude/skills/<name>/SKILL.md` | `@skill-name`, or automatic |
| OpenCode | `.opencode/skills/<name>/SKILL.md`, `.agents/skills/` or `.claude/skills/` | `skill({ name: "..." })` tool |
| Codex CLI | `.agents/skills/` plus an `AGENTS.md` line pointing at the folder | Agent reads `AGENTS.md` |
| Gemini CLI | `.agents/skills/` plus a `GEMINI.md` pointer | Agent reads `GEMINI.md` |
| Cursor | `.cursor/rules/<name>.mdc` (copy the `SKILL.md` body into the rule) | Rules are auto-attached |
| Windsurf | `.windsurf/rules/<name>.md` | Rules are auto-attached |
| GitHub Copilot | `.github/instructions/<name>.instructions.md` | Attached by rule scope |
| Cline | `.clinerules/<name>.md` | Auto-loaded |
| Roo Code | `.roo/rules/<name>.md` | Auto-loaded |
| Continue | `.continue/rules/<name>.md` | Auto-loaded |
| Aider | pass the file manually: `aider --read .agents/skills/name/SKILL.md` | Explicit read |
| Zed / any chat UI | paste the `SKILL.md` content into the prompt or context | Manual |

### Copy one skill

```bash
# macOS / Linux
mkdir -p .agents/skills
cp -r raw-skills/react-best-practices .agents/skills/

# Windows PowerShell
New-Item -ItemType Directory -Force .agents\skills | Out-Null
Copy-Item -Recurse raw-skills\react-best-practices .agents\skills\
```

### Copy everything

```bash
cp -r raw-skills/*-* .agents/skills/
```

Powerful but heavy: most agents will only surface descriptions, yet 1,963 entries still
cost tokens and can bury the skill you actually need. Prefer a curated subset.

---

## Skill anatomy

```markdown
---
name: my-skill-name
description: One sentence on what it does and when to use it.
---

# Skill Title

## When to use
## Instructions
## Examples
```

Rules that matter across agents:

- `name` must be lowercase, hyphen-separated, and match the folder name.
- `description` is the only thing the model sees before loading the skill - make it specific.
- Keep `SKILL.md` short; move long material into `references/` and link it.
- Scripts must be deterministic and must not require secrets.

---

## Notes

- Many folders carry their own `LICENSE` or attribution files (for example
  `loki-mode/LICENSE`). Where a bundled skill has its own license, that license wins for
  that folder. `MIT` here covers the collection as assembled.
- Some sample files contain placeholder credentials (`AKIAIOSFODNN7EXAMPLE`,
  `xoxb-YOUR-SLACK-BOT-TOKEN`). They are documentation examples, not live secrets. Never
  commit real keys to a fork.
- A few entries at the repository root are text placeholders that came from symlinks;
  they are harmless and point at relative paths.
- Descriptions were captured from each `SKILL.md` on 2026-11-05 - see [SKILLS.md](SKILLS.md).

---

## Contributing

1. Add one folder per skill with a `SKILL.md` (frontmatter `name` + `description`).
2. Keep helper scripts self-contained and secret-free.
3. Regenerate the index before opening a PR: `node scripts/build-index.mjs`.
4. Open a pull request describing the skill and when an agent should use it.

---

https://github.com/SHRIJANAGAIN/RAW-SKILLS.git
