# Create Project Memory Skills

Copy project-memory-store and project-memory-recall skills from templates to current project's `.claude/skills/` directory.

## Task

1. Check if `.claude/skills/` exists in current working directory, create if needed
2. Copy `~/.claude/skills/templates/project-memory-store/` to `.claude/skills/project-memory-store/`
3. Copy `~/.claude/skills/templates/project-memory-recall/` to `.claude/skills/project-memory-recall/`
4. Report completion with paths

## Notes

- These are project-specific memory skills - each project gets its own copy
- The templates are stored in `~/.claude/skills/templates/`
- coder-memory-store/recall are global (in `~/.claude/skills/`) and shared across all projects
- project-memory-store/recall are local (in `.claude/skills/`) and specific to each project
