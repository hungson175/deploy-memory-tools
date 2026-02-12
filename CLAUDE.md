# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MCP Server for Claude Code's persistent memory system. Provides semantic search over memories stored in Qdrant vector database with two-stage retrieval (previews first, full content on demand). Built with FastMCP.

## Development Commands

```bash
# Setup
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Run MCP server (requires Qdrant + embedding API key)
python -m qdrant_memory_mcp

# Linting & formatting
black src/
ruff check src/
ruff check --fix src/                # Auto-fix issues

# Type checking
mypy src/
```

**Prerequisites:**
- Qdrant running: `docker-compose up -d` (recommended) or `docker run -p 6333:6333 qdrant/qdrant`
- `.env` file with embedding provider API key (copy from `.env.example`)
  - OpenAI: `OPENAI_API_KEY=sk-...`
  - Voyage AI: `VOYAGE_API_KEY=...`
  - Set `EMBEDDING_PROVIDER` to choose provider (openai, voyage, nomic)

## Architecture

The main server implementation is in `src/qdrant_memory_mcp/__main__.py` (entry point and full server logic ~700 lines).

**Core flow:**
1. Lazy Qdrant client initialization via `get_qdrant_client()` - creates role-based collections on first access
2. Multi-provider embeddings via `_get_embedding()` with in-memory caching (`_embedding_cache` dict)
   - Supports OpenAI, Voyage AI, and Nomic providers
   - Configurable via `EMBEDDING_PROVIDER` environment variable
3. Two-stage retrieval: `search_memory()` returns previews only (title + description), `get_memory()`/`batch_get_memories()` fetch full content

### MCP Tools (7 total)

| Tool | Purpose |
|------|---------|
| `search_memory` | Semantic search, returns previews only |
| `get_memory` | Full content by ID |
| `batch_get_memories` | Multi-fetch by IDs |
| `store_memory` | Create new memory |
| `update_memory` | Update existing (re-embeds) |
| `delete_memory` | Remove by ID |
| `list_collections` | Show all collections with counts |

### Collection Naming

Global collections map to roles defined in `ROLE_COLLECTIONS` (`__main__.py:72-83`):
- `universal-patterns`, `backend-patterns`, `frontend-patterns`, `quant-patterns`, `devops-patterns`, `ml-patterns`, `security-patterns`, `mobile-patterns`, `ai-patterns`, `scrum-master-patterns`

Project collections: `proj-{sanitized-project-name}` (auto-created on first store)

### Memory Document Format

```
**Title:** <concise title>
**Description:** <one sentence summary>

**Content:** <full memory text>

**Tags:** #tag1 #tag2
```

Preview extraction in `search_memory()` reads `title` and `description` directly from metadata payload.

## Key Design Decisions

1. **Logging to stderr** - Required for stdio MCP transport; stdout reserved for JSON-RPC
2. **Lazy Qdrant init** - Client created on first tool call, not server start
3. **Embedding cache** - In-memory dict prevents repeated API calls for same text
4. **Two-stage retrieval** - ~60% token savings by returning only previews in search results

## Configuration

Environment variables (loaded from `.env`):
- `QDRANT_URL` - Qdrant server URL (default: `http://localhost:6333`)
- `EMBEDDING_PROVIDER` - Embedding provider: `openai`, `voyage`, or `nomic` (default: `openai`)
- `OPENAI_API_KEY` - Required if using OpenAI embeddings
- `VOYAGE_API_KEY` - Required if using Voyage AI embeddings
- `EMBEDDING_MODEL` - Override default model for chosen provider
- `EMBEDDING_DIMENSION` - Override default embedding dimension

MCP config in `~/.claude.json`:
```json
{
  "mcpServers": {
    "memory": {
      "type": "stdio",
      "command": "python3",
      "args": ["/path/to/src/qdrant_memory_mcp/__main__.py"],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "OPENAI_API_KEY": "sk-..."
      }
    }
  }
}
```

## Installation

For end users, use the one-command installation:
```bash
git clone https://github.com/hungson175/deploy-memory-tools.git
cd deploy-memory-tools
./install.sh
```

This installs:
- Python package (qdrant-memory-mcp)
- Docker container running Qdrant
- Skills (coder-memory-recall, coder-memory-store) → `~/.claude/skills/`
- Memory-only subagent → `~/.claude/subagents/`
- MCP server configuration → `~/.claude.json`

See `install.sh` for details. Uninstall with `./uninstall.sh`.

## Important Note

**Don't waste time researching memory mechanisms.** The current system (Qdrant + multi-provider embeddings) is good enough. Big companies will release deeply integrated LLM memory solutions soon - wait for those instead of over-engineering external layers.

## Claude's Role in This Project

**You are a light assistant for:**

1. **Memory Issues** - Help with this memory system implementation
2. **Project Management** - Act as Scrum Product Owner (PO) for this project

### Project Management Responsibilities

**Maintain `docs/BACKLOG.md` as a PO:**
- Organize tasks by priority: P0 (Critical), P1 (High), P2 (Medium), P3 (Low)
- Keep backlog updated with new tasks, bugs, and ideas
- Ensure priorities reflect actual importance
- Track task status (Not Started, In Progress, Blocked, Done)
- **See `docs/BACKLOG.md` for current task list and priorities**

**Scrum PO mindset:**
- P0: Critical bugs blocking functionality
- P1: High-value features or important bugs
- P2: Medium priority improvements
- P3: Nice-to-have or cleanup tasks

**When working on tasks:**
- Update backlog status in `docs/BACKLOG.md`
- Move completed items to archive or mark as Done
- Add new tasks discovered during work
- Reprioritize as needed based on user feedback
- Reference `LOG_BUGES.md` for known bugs and fixes

## Directory Structure

```
deploy-memory-tools/
├── src/qdrant_memory_mcp/   # Main package
│   ├── __main__.py          # Entry point + all server logic
│   ├── config.py            # Configuration helpers
│   └── utils/               # Embedding + sanitization helpers
├── skills/                  # Claude Code skills
│   ├── coder-memory-recall/ # Retrieve memories before tasks
│   └── coder-memory-store/  # Store learnings after tasks
├── subagents/memory-only/   # Subagent with only MCP memory tools
├── docs/
│   ├── BACKLOG.md           # Priority task list (check first!)
│   ├── blogpost/            # Blog post drafts
│   ├── reviews/             # Code reviews
│   └── tmux/                # Multi-agent team config
├── .claude/                 # Project-specific commands/hooks
├── install.sh               # One-command installation
├── uninstall.sh             # Clean uninstallation
└── LOG_BUGES.md             # Known bugs and fixes
```
