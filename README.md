# Claude Code Memory Tools

Give Claude Code memory that works across projects - it learns from your coding sessions and remembers solutions.

## Installation

1. **Copy this directory** to your working project
2. **Open Claude Code** in that project
3. **Run**: `execute guide in ./deploy-memory-tools/install.md`
4. **Wait** for completion
5. **Restart Claude Code** (exit and reopen)

Done! Claude now has memory in this project AND globally across all projects.

## Usage

**Store memory** (Claude decides scope):
```
--learn
```

**Recall memory** (Claude decides scope):
```
--recall
```

**Manual control**:
- `--coder-store` - Store universal patterns
- `--project-store` - Store project-specific insights
- `--coder-recall` - Recall universal patterns
- `--project-recall` - Recall project-specific insights

## What Gets Installed

**Global Skills** (all projects):
- `coder-memory-store` / `coder-memory-recall`

**Project-specific Skills**:
- `project-memory-store` / `project-memory-recall`

## For New Projects

1. Open Claude Code in new project
2. Run: `/create-project-memory-skills`
3. Restart Claude Code

## Details

See [QUICKSTART.md](./QUICKSTART.md) for technical details.
