# Migration Guide: V3.2 → Reorganized V2 Structure

This guide helps you migrate from the old V3.2 structure to the new standardized Python MCP server structure.

## What Changed

### Directory Structure

**Before:**
```
deploy-memory-tools/
├── qdrant_memory_mcp_server_v2.py  # Monolithic file
├── global/                          # V3 skills
├── templates/                       # V3 templates
└── docs/                            # Mixed documentation
```

**After:**
```
deploy-memory-tools/
├── src/qdrant_memory_mcp/          # Proper Python package
│   ├── __init__.py
│   ├── __main__.py
│   ├── server.py
│   ├── config.py
│   └── utils/
├── tests/                           # Test suite
├── docs/                            # Organized docs
├── backup/                          # Old versions
└── pyproject.toml                   # Python packaging
```

## Migration Steps

### 1. Update Your Installation

```bash
cd /path/to/deploy-memory-tools

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
uv pip install -e .
```

### 2. Update Configuration

Your `.env` file stays the same, but update your `~/.claude.json`:

**Old path:**
```json
{
  "mcpServers": {
    "memory": {
      "command": "python3",
      "args": [
        "/path/to/deploy-memory-tools/qdrant_memory_mcp_server_v2.py"
      ]
    }
  }
}
```

**New path:**
```json
{
  "mcpServers": {
    "memory": {
      "command": "python3",
      "args": [
        "/path/to/deploy-memory-tools/src/qdrant_memory_mcp/__main__.py"
      ],
      "env": {
        "QDRANT_URL": "http://your-server:6309",
        "OPENAI_API_KEY": "sk-proj-..."
      }
    }
  }
}
```

### 3. Test the Migration

```bash
# Run the server
python -m qdrant_memory_mcp

# Test MCP tools (in another terminal or via Claude Code)
# Should connect to your existing Qdrant database
```

### 4. Verify Data Integrity

Your Qdrant data (`qdrant_storage/`) remains unchanged. All collections and memories are preserved:

- `universal-patterns`
- `backend-patterns`
- `frontend-patterns`
- etc.

## Rollback (If Needed)

If you encounter issues, the old version is preserved in `backup/v3.2/`:

```bash
# Restore old server
cp backup/v3.2/qdrant_memory_mcp_server_v2.py ./

# Update ~/.claude.json back to old path
```

## Benefits of New Structure

1. **Standard Python Package** - Follows Python packaging best practices
2. **Modular Code** - Separated concerns (config, utils, server logic)
3. **Better Testing** - Dedicated test directory
4. **Development Mode** - Install with `pip install -e .`
5. **Type Checking** - Ready for mypy and other tools
6. **Documentation** - Organized docs structure

## Getting Help

If you encounter issues:

1. Check the logs in stderr (configured in `config.py`)
2. Verify Qdrant is accessible
3. Confirm environment variables are set
4. Review the updated README.md

## References

- [README.md](../../README.md) - Main documentation
- [QUICKSTART.md](../../QUICKSTART.md) - Quick start guide
- [CLAUDE.md](../../CLAUDE.md) - Project overview
