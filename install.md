# Installation Instructions for Claude Code

Execute these steps to install the Human-Like Memory Skills.

## Task

1. **Install Global Skills** (user-level, shared across all projects):
   - Copy `deploy/global/coder-memory-store/` to `~/.claude/skills/coder-memory-store/`
   - Copy `deploy/global/coder-memory-recall/` to `~/.claude/skills/coder-memory-recall/`

2. **Install Templates** (for creating project-specific skills):
   - Create directory `~/.claude/skills/templates/` if it doesn't exist
   - Copy `deploy/templates/project-memory-store/` to `~/.claude/skills/templates/project-memory-store/`
   - Copy `deploy/templates/project-memory-recall/` to `~/.claude/skills/templates/project-memory-recall/`

3. **Install Command**:
   - Create directory `~/.claude/commands/` if it doesn't exist
   - Copy `deploy/commands/create-project-memory-skills.md` to `~/.claude/commands/create-project-memory-skills.md`

4. **Initialize Project Memory** (in current working directory):
   - Execute the `/create-project-memory-skills` command
   - This copies templates from `~/.claude/skills/templates/` to `.claude/skills/` in current project

5. **Report Completion**:
   - List what was installed and where
   - Remind user to restart Claude Code

## Success Criteria

After installation:
- `~/.claude/skills/coder-memory-store/SKILL.md` exists
- `~/.claude/skills/coder-memory-recall/SKILL.md` exists
- `~/.claude/skills/templates/project-memory-store/SKILL.md` exists
- `~/.claude/skills/templates/project-memory-recall/SKILL.md` exists
- `~/.claude/commands/create-project-memory-skills.md` exists
- `.claude/skills/project-memory-store/SKILL.md` exists (in current project)
- `.claude/skills/project-memory-recall/SKILL.md` exists (in current project)

## Next Steps

Tell user to:
1. Restart Claude Code to load new skills
2. Read QUICKSTART.md for usage instructions
3. Try: `--coder-store` or `--project-store` after completing a task
