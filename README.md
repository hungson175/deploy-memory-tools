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

### One-Command Installation (Recommended)

Install everything (MCP server, Docker + Qdrant, skills, subagent, config) with one command:

```bash
git clone https://github.com/hungson175/deploy-memory-tools.git
cd deploy-memory-tools
./install.sh
```

**What it installs:**
- ✅ Python package (qdrant-memory-mcp)
- ✅ Docker container running Qdrant
- ✅ Skills (coder-memory-recall, coder-memory-store)
- ✅ Memory-only subagent
- ✅ MCP server configuration in ~/.claude.json
- ✅ Environment setup (.env file)

**Requirements:**
- Docker (running)
- Python 3.10+
- Claude Code

**After installation:**
1. Add your OpenAI API key to `.env`
2. Restart Claude Code
3. Memory system auto-triggers on complex tasks

### Manual Installation (Advanced)

<details>
<summary>Click to expand manual installation steps</summary>

#### 1. Install Python Package

```bash
# Using uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Or using pip
pip install -e .
```

#### 2. Start Qdrant

```bash
docker-compose up -d
```

#### 3. Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

#### 4. Install Skills & Subagent

```bash
# Copy skills
cp -r skills/coder-memory-recall ~/.claude/skills/
cp -r skills/coder-memory-store ~/.claude/skills/

# Copy subagent
cp -r subagents/memory-only ~/.claude/subagents/
```

#### 5. Update ~/.claude.json

See "Configuration for Claude Code" section below.

</details>

### Uninstall

```bash
./uninstall.sh
```

## Project Structure

```
deploy-memory-tools/
├── src/qdrant_memory_mcp/     # Main package
│   ├── __main__.py            # Entry point + server logic
│   ├── config.py              # Configuration
│   └── utils/                 # Helper utilities
├── skills/                    # Claude Code skills
├── subagents/                 # Memory-only subagent
├── docs/                      # Documentation & backlog
├── install.sh                 # One-command installation
├── uninstall.sh               # Uninstallation
└── pyproject.toml             # Python project config
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

- [Project Documentation](CLAUDE.md)

## License

MIT
