# Installation Instructions for Claude Code

Execute these steps to install the Human-Like Memory Skills.

## CRITICAL: Avoid Stacked Directories

**WRONG** (creates nested directories):
```bash
cp -r deploy/global/coder-memory-store ~/.claude/skills/
# Results in: ~/.claude/skills/coder-memory-store/coder-memory-store/SKILL.md ❌
```

**CORRECT** (flat structure):
```bash
mkdir -p ~/.claude/skills/coder-memory-store
cp -r deploy/global/coder-memory-store/* ~/.claude/skills/coder-memory-store/
# Results in: ~/.claude/skills/coder-memory-store/SKILL.md ✅
```

Always use `source/*` to copy CONTENTS only, not the directory itself.

## Task

1. **Install Global Skills** (user-level, shared across all projects):
   ```bash
   mkdir -p ~/.claude/skills/coder-memory-store
   cp -r deploy/global/coder-memory-store/* ~/.claude/skills/coder-memory-store/

   mkdir -p ~/.claude/skills/coder-memory-recall
   cp -r deploy/global/coder-memory-recall/* ~/.claude/skills/coder-memory-recall/
   ```

2. **Install Templates** (for creating project-specific skills):
   ```bash
   mkdir -p ~/.claude/skills/templates/project-memory-store
   cp -r deploy/templates/project-memory-store/* ~/.claude/skills/templates/project-memory-store/

   mkdir -p ~/.claude/skills/templates/project-memory-recall
   cp -r deploy/templates/project-memory-recall/* ~/.claude/skills/templates/project-memory-recall/
   ```

3. **Install Command**:
   ```bash
   mkdir -p ~/.claude/commands
   cp deploy/commands/create-project-memory-skills.md ~/.claude/commands/create-project-memory-skills.md
   ```

4. **Initialize Project Memory** (in current working directory):
   ```bash
   mkdir -p .claude/skills/project-memory-store
   cp -r ~/.claude/skills/templates/project-memory-store/* .claude/skills/project-memory-store/

   mkdir -p .claude/skills/project-memory-recall
   cp -r ~/.claude/skills/templates/project-memory-recall/* .claude/skills/project-memory-recall/
   ```
   OR just execute `/create-project-memory-skills` command after restart

5. **Report Completion**:
   - List what was installed and where
   - Verify with `ls` commands that structure is FLAT (no nested directories)
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
