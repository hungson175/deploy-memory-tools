# Qdrant Memory MCP Server V2

MCP Server for semantic memory storage with Qdrant vector database and two-stage retrieval.

## Features

- ✅ Two-stage retrieval (preview → full content)
- ✅ Role-based memory collections (universal, backend, frontend, etc.)
- ✅ Semantic search via OpenAI embeddings
- ✅ Remote or local Qdrant support
- ✅ Project-specific and global memory storage
- ✅ CRUD operations for memories

## Quick Start

### 1. Installation

```bash
# Using uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Or using pip
pip install -e .
```

### 2. Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Run the Server

```bash
python -m qdrant_memory_mcp
```

## Project Structure

```
deploy-memory-tools/
├── src/
│   └── qdrant_memory_mcp/     # Main package
│       ├── __init__.py         # Package initialization
│       ├── __main__.py         # Entry point
│       ├── server.py           # Server logic
│       ├── config.py           # Configuration
│       └── utils/              # Utilities
│           ├── embeddings.py   # OpenAI embedding functions
│           └── sanitize.py     # Collection name sanitization
├── tests/                      # Test suite
├── docs/                       # Documentation
├── backup/                     # Old versions backup
├── pyproject.toml             # Python project config
├── .env.example               # Environment template
└── README.md                  # This file
```

## MCP Tools

The server provides 7 MCP tools:

1. `list_collections` - List all memory collections
2. `search_memory` - Semantic search (returns previews)
3. `get_memory` - Get full memory by ID
4. `batch_get_memories` - Get multiple memories efficiently
5. `store_memory` - Store new memory
6. `update_memory` - Update existing memory
7. `delete_memory` - Delete memory

## Memory Collections

### Global Collections (Role-Based)
- `universal-patterns` - Cross-domain patterns
- `backend-patterns` - Backend engineering
- `frontend-patterns` - Frontend development
- `quant-patterns` - Quantitative finance
- `devops-patterns` - DevOps & infrastructure
- `ml-patterns` - Machine learning
- `security-patterns` - Security engineering
- `mobile-patterns` - Mobile development

### Project Collections
- `proj-{project-name}` - Project-specific memories

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/ tests/
ruff check src/ tests/
```

### Type Checking

```bash
mypy src/
```

## Configuration for Claude Code

Add to your `~/.claude.json`:

```json
{
  "mcpServers": {
    "memory": {
      "type": "stdio",
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

## Documentation

- [Quick Start Guide](QUICKSTART.md)
- [Project Documentation](CLAUDE.md)
- [Migration Guides](docs/guides/)

## License

MIT
