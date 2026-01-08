# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MCP Server for Claude Code's persistent memory system. Provides semantic search over memories stored in Qdrant vector database with two-stage retrieval (previews first, full content on demand). Built with FastMCP.

## Development Commands

```bash
# Setup
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Run MCP server (requires Qdrant + OpenAI API key)
python -m qdrant_memory_mcp

# Testing
pytest tests/                        # Run all tests
pytest tests/test_foo.py             # Run single test file
pytest tests/test_foo.py::test_bar   # Run single test function

# Linting & formatting
black src/ tests/
ruff check src/ tests/
ruff check --fix src/ tests/         # Auto-fix issues

# Type checking
mypy src/
```

**Prerequisites:**
- Qdrant running: `docker run -p 6333:6333 qdrant/qdrant`
- `.env` file with `OPENAI_API_KEY` (copy from `.env.example`)

## Architecture

The main server implementation is in `src/qdrant_memory_mcp/__main__.py` (entry point and full server logic). Note: `server.py` is a duplicate of `__main__.py`.

**Core flow:**
1. Lazy Qdrant client initialization via `get_qdrant_client()` - creates role-based collections on first access
2. OpenAI embeddings via `_get_embedding()` with in-memory caching (`_embedding_cache` dict)
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

Global collections map to roles defined in `ROLE_COLLECTIONS` (`__main__.py:41-51`):
- `universal-patterns`, `backend-patterns`, `frontend-patterns`, `quant-patterns`, `devops-patterns`, `ml-patterns`, `security-patterns`, `mobile-patterns`, `ai-patterns`

Project collections: `proj-{sanitized-project-name}` (auto-created on first store)

### Memory Document Format

```
**Title:** <concise title>
**Description:** <one sentence summary>

**Content:** <full memory text>

**Tags:** #tag1 #tag2
```

Preview extraction in `_extract_preview()` parses Title and Description for two-stage retrieval.

## Key Design Decisions

1. **Logging to stderr** - Required for stdio MCP transport; stdout reserved for JSON-RPC
2. **Lazy Qdrant init** - Client created on first tool call, not server start
3. **Embedding cache** - In-memory dict prevents repeated API calls for same text
4. **Two-stage retrieval** - ~60% token savings by returning only previews in search results

## Configuration

Environment variables (loaded from `.env`):
- `QDRANT_URL` - Qdrant server URL (default: `http://localhost:6333`)
- `OPENAI_API_KEY` - Required for embeddings

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

## Important Note

**Don't waste time researching memory mechanisms.** The current system (Qdrant + Voyage AI) is good enough. Big companies will release deeply integrated LLM memory solutions soon - wait for those instead of over-engineering external layers.

## Other

- `backup/` - Deprecated legacy versions (ignore)
- `commands/` - Claude Code slash commands
- `docs/` - Design docs and guides
