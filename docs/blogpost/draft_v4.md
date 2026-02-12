# Memory for Claude Code: A Practical Guide

**DRAFT V4**

---

## The Problem

Claude Code keeps forgetting everything - repeats the same bugs daily. Not very useful.

**Memory solves that problem.** With memory, coding agents become self-improving, like humans. The more they work, the more bugs they encounter, the more experience they accumulate, the better they get.

---

## The Solution

I've created a memory package that you can install and use directly with Claude Code. One command, everything works.

**Just want to use it?** Skip to the installation link at the end.

**Want to understand how it works?** Keep reading.

---

# How It Works (Optional)

---

## 1. How: Storage Mechanism

### Theory

People debate page indexes, tree structures, knowledge graphs. But here's the thing: when Google or Anthropic drops a new technology, it won't be 20-30% better or even double. It'll blow everything out of the water - makes all our current approaches irrelevant. So arguing over 5-10-20% differences? Pointless.

### Our Implementation

**Simple:** Files + Qdrant vector database.

```mermaid
graph LR
    A[Memory] --> B[Document Format]
    A --> C[Vector Embedding]
    B --> D[Qdrant Collection]
    C --> D
    D --> E[Role-based Collections]
    E --> F[universal-patterns]
    E --> G[backend-patterns]
    E --> H[frontend-patterns]
    E --> I[ai-patterns]
```

**Key design:**
- MCP server (`src/qdrant_memory_mcp/__main__.py`)
- **Mini search engine** (two-stage retrieval like Google):
  - First: Return 20-50 previews (50-100 tokens each, like Google snippets)
  - LLM reviews all snippets and picks relevant ones (e.g., docs 2, 20, 50)
  - Then: Fetch only 3-4 full documents
  - **Why?** Vector search finds similarity, not relevance. LLM (Claude) decides relevance way better than dumb rankings.
- Role-based collections: backend, frontend, AI, etc.
- In-memory embedding cache (prevents repeated API calls)

**Algorithm:**
1. Search → Get 20 results
2. Return only titles + descriptions (2-3 sentences each)
3. LLM reads 50 snippets, picks best 3-5
4. Fetch full content only for those
5. Result: Consider 50 items but only load 3-4 full docs

**References:**

*Papers we use:*
- **Reasoning Bank** (Google, Sept 2025) - test-time scaling
- **LangChain Agent Memory Paper** - episodic, semantic, procedural

*Other approaches (work but I don't care):*
- Page Index, Knowledge Graph, Hinsight article on memory

---

## 2. What: Content to Store

### Theory

**First rule: Storing every specific memory is garbage and not useful.**

LangGraph defines three memory types: episodic, semantic, procedural.

### Our Implementation

**Extract both episodic AND semantic at the same time** when a bug is encountered.

```mermaid
graph TD
    A[Bug Encountered] --> B[Extract Both Types]
    B --> C[Episodic + TTL]
    B --> D[Semantic Pattern]
    C --> E[Dies Later]
    D --> F[Stays Forever]
    style F fill:#90EE90
    style E fill:#FFB6C1
```

**Example:**

**Hit Binance API rate limit** → locked out for hours

Store both simultaneously:

**Episodic (with TTL):**
```
Binance API hit rate limit of 1200 requests/minute
See file: binance_crawler.py
Tags: #backend #api #binance #rate-limit
```

**Semantic (permanent):**
```
For external APIs, always check rate limits before deployment
Tags: #backend #api #best-practice
```

**In our code:**
- Episodic: `memory_type: "episodic"` with TTL metadata
- Semantic: `memory_type: "semantic"` (no expiration)
- Procedural: `memory_type: "procedural"` (workflows) - **extremely special**, implemented differently

**Procedural memory note:**
Very special. Agents self-update their markdown files directly. They self-improve over time through workflow refinement.

**Skills that handle this:**
- `coder-memory-store` - auto-extracts semantic from episodic
- `coder-memory-recall` - uses mini search engine to find relevant memories

---

## 3. When: Trigger Conditions

### Theory

Most papers ignore "when" entirely. But in practice, it's the hardest question.

### Our Implementation

**Two triggers in Claude Code:**

#### When to STORE?

**After task completes** (end of while loop)

**Storage process:**

```mermaid
graph TD
    A[Task Complete] --> B[Search Similar Memories]
    B --> C{Similar Found?}
    C -->|Yes| D[Merge/Update/Delete]
    C -->|No| E[Store New Memory]
    D --> F[Memory Clean]
    E --> F
```

1. **Search for similar memories first** (mini search engine)
2. **If similar found:** Merge, reinforce, update, or delete conflicting (prioritize newer)
3. **If nothing similar:** Store as new
4. **Result:** Prevents endless growth and memory pollution

**Why this matters:** Without duplicate checking, memory grows endlessly and gets polluted. Becomes useless garbage.

**Implementation:**
- Hook: `~/.claude/hooks/memory_store_reminder.py`
- Triggers after task completion
- Uses mini search engine to check duplicates
- Random sampling (1/3 chance) to reduce noise

**Learn more:** [Claude Code Hooks Documentation]

#### When to RETRIEVE?

**When planning tool is called** (`TodoWrite`)

```mermaid
sequenceDiagram
    User->>Claude: Complex task
    Claude->>TodoWrite: Create plan
    TodoWrite->>Hook: Post-tool-use
    Hook->>Memory: Mini search engine
    Memory->>Claude: Return 50 snippets
    Claude->>Memory: Fetch full docs 2, 20, 50
    Memory->>Claude: Full content
    Claude->>User: Execute with memory
```

**Why this works:**
- **Selective** - Only complex tasks call TodoWrite
- **Context-aware** - Agent knows what it needs when planning
- **Perfect timing** - Right before execution

**Implementation:**
- Skill: `coder-memory-recall` (triggered by complex tasks)
- Subagent: `memory-only` (MCP tools only, no file access)
- Hook on TodoWrite post-tool-use
- Mini search engine returns snippets → LLM picks relevant → fetch full

**Learn more:** [Claude Code Hooks Documentation]

---

## Quick Summary

| Question | Theory | Our Implementation |
|----------|--------|-------------------|
| **How** | Files/Vector/Graph | Qdrant + MCP + mini search engine (2-stage) |
| **What** | Episodic/Semantic/Procedural | Extract both episodic+semantic simultaneously, check duplicates before storing |
| **When (Store)** | Various approaches | After task completes (hook on completion) |
| **When (Retrieve)** | Often ignored | When TodoWrite called (mini search → LLM picks → fetch) |

---

## Architecture Overview

```mermaid
graph TB
    A[Claude Code] --> B[Skills]
    A --> C[Hooks]
    B --> D[coder-memory-recall]
    B --> E[coder-memory-store]
    C --> F[Post TodoWrite]
    C --> G[Post Completion]
    D --> H[memory-only subagent]
    E --> H
    H --> I[MCP Server]
    I --> J[Qdrant Vector DB]
    J --> K[Role Collections]
    I --> L[Mini Search Engine]
    L --> M[Preview Snippets]
    L --> N[Full Documents]
```

**Components:**
- **MCP Server** - Memory operations via tools
- **Qdrant** - Vector database (Docker container)
- **Mini Search Engine** - Two-stage retrieval (snippets → LLM picks → full docs)
- **Skills** - Auto-trigger recall/store
- **Subagent** - MCP-only (prevents file pollution)
- **Hooks** - Timing triggers

---

## Installation

**One-command install includes:**
- MCP server
- Docker + Qdrant (auto-start)
- Skills (`coder-memory-recall`, `coder-memory-store`)
- Subagent (`memory-only`)
- Configuration (`~/.claude.json`)

**Installation link:** [To be added when package is ready]

---

## Don't Over-Engineer

Memory is THE hot topic (end 2025 → biggest 2026). Anthropic has memory in beta. Google has papers on solving it at the LLM level.

**My advice:** Simple, working solutions beat complex optimizations. The big players will release model-layer memory soon that'll make everything else irrelevant.

If there's memory, coding agents become self-improving. But don't waste time over-engineering.

---

## What's Next

- Installation package (one command)
- Source code release (reverse-engineered Claude Code - separate post)
- Autonomous team framework (memory is the real power)

---

**Written:** 2026-01-13
**Status:** DRAFT V4 - Refined implementation details and wording
