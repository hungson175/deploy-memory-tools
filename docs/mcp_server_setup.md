# MCP Server Setup for Memory Skills

## Overview

The Qdrant Memory MCP server provides 5 tools for Claude Code to interact with the vector database:
- `search_memory()` - Semantic search for similar memories
- `store_memory()` - Insert new memory
- `update_memory()` - Update existing memory (regenerates embedding)
- `get_memory()` - Retrieve memory by ID
- `delete_memory()` - Delete memory by ID

## Prerequisites

1. **Qdrant running**: Docker container on localhost:6333
2. **Python dependencies**: fastmcp, qdrant-client, openai, python-dotenv
3. **OpenAI API key**: Set in `.env` file

## Installation

### 1. Install Python dependencies

```bash
cd /Users/sonph36/dev/deploy-memory-tools
pip install fastmcp qdrant-client openai python-dotenv
```

### 2. Verify .env file

Ensure `.env` contains your OpenAI API key:

```bash
OPENAI_API_KEY=sk-...
```

### 3. Test MCP server

```bash
python3 qdrant_memory_mcp_server.py
```

## Configure in Claude Code

Add to your Claude Code MCP configuration (usually `~/.config/claude/mcp.json` or similar):

```json
{
  "mcpServers": {
    "memory": {
      "command": "python3",
      "args": ["/Users/sonph36/dev/deploy-memory-tools/qdrant_memory_mcp_server.py"]
    }
  }
}
```

## Tool Documentation

### search_memory(query, memory_level, limit=5)

Search for similar memories using semantic search.

**Parameters**:
- `query` (str): 2-3 sentence summary of what you're looking for
- `memory_level` (str): "coder" for global, "project" for current project
- `limit` (int): Maximum results (default: 5)

**Returns**: Formatted results with file paths, similarity scores, metadata

**Example**:
```python
search_memory(
    query="How to handle pytest fixtures for database testing with proper cleanup",
    memory_level="coder",
    limit=5
)
```

---

### store_memory(document, metadata, memory_level)

Insert new memory into vector database.

**Parameters**:
- `document` (str): Full formatted memory (Title + Description + Content + Tags)
- `metadata` (dict): Must contain:
  - `memory_type`: "episodic" | "procedural" | "semantic"
  - `file_path`: Relative path from skill root
  - `skill_root`: "coder-memory-store" or "project-memory-store"
  - `tags`: List of tags (e.g., ["success", "pytest"])
  - `title`: Memory title
  - `created_at`: ISO timestamp
  - `last_synced`: ISO timestamp
- `memory_level` (str): "coder" or "project"

**Returns**: JSON with document ID and status

**Example**:
```python
store_memory(
    document="**Title:** Pytest Fixture Pattern...",
    metadata={
        "memory_type": "procedural",
        "file_path": "procedural/testing.md",
        "skill_root": "coder-memory-store",
        "tags": ["pytest", "testing"],
        "title": "Pytest Fixture Pattern",
        "created_at": "2025-10-30T...",
        "last_synced": "2025-10-30T..."
    },
    memory_level="coder"
)
```

---

### update_memory(doc_id, document, metadata, memory_level)

Update existing memory (regenerates embedding).

**Parameters**: Same as store_memory, plus:
- `doc_id` (str): UUID of memory to update

**Returns**: Success message or error

**Note**: This does delete + insert with same ID, regenerating embedding.

---

### get_memory(doc_id, memory_level)

Retrieve full memory by ID.

**Parameters**:
- `doc_id` (str): UUID of memory
- `memory_level` (str): "coder" or "project"

**Returns**: Full memory document and metadata

**Use case**: Read existing memory before merging during consolidation.

---

### delete_memory(doc_id, memory_level)

Delete memory by ID.

**Parameters**:
- `doc_id` (str): UUID of memory
- `memory_level` (str): "coder" or "project"

**Returns**: Success message with updated points count

**Use case**: Remove duplicate during MERGE consolidation.

---

## Collection Naming

- **Global memories**: `coder-memory`
- **Project memories**: `proj-{sanitized-project-name}`
  - Example: `proj-deploy-memory-tools`
  - Sanitized: lowercase alphanumeric + hyphens only

Collections are auto-created on first use.

---

## Testing the Server

### 1. Search for memories

```python
# In Claude Code after MCP server is configured
search_memory(
    query="pytest fixtures database testing",
    memory_level="coder",
    limit=3
)
```

### 2. Insert a test memory

```python
store_memory(
    document="**Title:** Test Memory\n**Description:** Testing MCP server\n\n**Content:** This is a test.\n\n**Tags:** #test",
    metadata={
        "memory_type": "episodic",
        "file_path": "test.md",
        "skill_root": "coder-memory-store",
        "tags": ["test"],
        "title": "Test Memory",
        "created_at": "2025-10-30T13:00:00Z",
        "last_synced": "2025-10-30T13:00:00Z"
    },
    memory_level="coder"
)
```

### 3. Verify in Qdrant

```bash
curl -s http://localhost:6333/collections/coder-memory | python3 -m json.tool
```

---

## Troubleshooting

### MCP server not showing in Claude Code

1. Check MCP configuration file path
2. Verify Python path is correct
3. Restart Claude Code after configuration changes

### Search returns no results

1. Verify collection exists: `curl http://localhost:6333/collections`
2. Check points count: `curl http://localhost:6333/collections/coder-memory`
3. Run sync if needed: `./sync_memories.sh`

### Embedding errors

1. Check OpenAI API key in `.env`
2. Verify API key has credits
3. Test OpenAI connection:
   ```python
   from openai import OpenAI
   import os
   from dotenv import load_dotenv
   load_dotenv()
   client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
   response = client.embeddings.create(input="test", model="text-embedding-3-small")
   print(response.data[0].embedding[:5])
   ```

---

## Development Notes

- **Embedding model**: text-embedding-3-small (1536 dimensions)
- **Distance metric**: Cosine similarity (higher = more similar)
- **Auto-collection creation**: Collections created on first use
- **Memory level routing**: Automatic based on parameter
- **Update = Upsert**: Same ID, new vector (regenerates embedding)
