# Memory for Claude Code: A Practical Guide

**DRAFT V2**

---

## The Problem

Claude Code is brilliant but has amnesia - forgets everything daily, repeats the same bugs. Not very useful.

**Memory solves that problem.**

---

## The Solution

I've created a memory package that you can install and use directly with Claude Code. One command, everything works.

**Just want to use it?** Skip to the installation link at the end.

**Want to understand how it works?** Keep reading.

---

# How It Works (Optional)

---

## 1. How: Storage Mechanism

**Short answer:** Files + vector database.

People argue about page indexes, tree structures, knowledge graphs. **Who cares?** Differences of 10-20% don't matter when next year Google releases something better anyway.

Pick something that works. Move on.

---

## 2. What: Content to Store

**First rule: Storing every single memory specifically is garbage and not useful.**

If you store "Binance API rate limit is 1200 req/min, see binance_crawler.py", what happens three days later when that file changes? Your memory is now garbage. **Memory must generalize to stay useful.**

### Three Types of Memory

From the LangGraph memory paper:

**1. Episodic (Specific + TTL)**
- Concrete events with expiration date
- Must have Time-To-Live (TTL) - dies after a while
- Prevents outdated specifics from polluting database

**2. Semantic (Generalized)**
- Universal patterns extracted from episodic experiences
- Stays relevant across contexts
- Example: "External APIs require rate limit consideration"

**3. Procedural (Workflows)**
- Team processes and workflows
- Very special - critical for self-improvement
- See ACE: Agentic Context Engineering (Oct 2025) for implementation

### Example Flow

**1. Hit Binance API rate limit**
- Specific bug: locked out for several hours

**2. Store episodic memory with TTL**
- "Binance API hit rate limit of 1200 requests per minute, see file binance_crawler.py"
- This memory will expire

**3. Extract semantic pattern**
- "For external APIs, check rate limits"
- This stays useful forever

**Why generalization matters:** Specific memories decay. General patterns stay relevant. Store both, but know the difference.

---

## 3. When: Trigger Conditions

**This is the hardest question.** Two parts:

### When to STORE?

**Simple:** After the task completes.

Claude Code runs in a while loop (~10 lines of code). When finished, ask: "Anything worth storing?" Full context is still there.

Optional: Use random sampling (I use 1/3 chance) to reduce noise.

### When to RETRIEVE?

**The clever solution:** Hook on the planning tool.

Claude Code calls `TodoWrite` when starting complex tasks. That's your trigger.

**Why this works:**
1. **Selective** - Only complex tasks trigger retrieval
2. **Context-aware** - Agent knows what it needs when planning
3. **Perfect timing** - Right when outlining "research X, implement Y, test Z"

**Implementation:** Use Claude Code's hooks system. Hook on `TodoWrite` post-tool-use.

**Learn more about Claude Code hooks:** [See hooks documentation article]

---

## Quick Summary

| Question | Answer |
|----------|--------|
| **How** | Files + Vector DB |
| **What** | Episodic (TTL) + Semantic (generalized) + Procedural (workflows) |
| **When (Store)** | After task completes |
| **When (Retrieve)** | When planning tool is called |

---

## My Implementation

Simple architecture. No fancy stuff. It works.

- Qdrant vector database
- MCP server for Claude Code integration
- Role-based collections (backend, frontend, AI, etc.)
- Two-stage retrieval (previews first, full content on demand)

---

## Don't Over-Engineer

**Reality check:** Memory is THE hot topic (end 2025 → biggest 2026). Anthropic has memory in beta. Google has papers on solving it at the LLM level.

**My advice:** Implement simple, working solutions. Don't spend months optimizing. The big players will release model-layer memory soon, and our external engineering will become obsolete.

If there's memory, coding agents transform completely. But don't waste time over-engineering.

---

## Installation

**Coming soon:** One-command installation package including:
- MCP server
- Docker + Qdrant (auto-start)
- Skills (coder-memory-recall, coder-memory-store)
- Subagent (memory-only)
- Complete configuration

**Installation link:** [To be added when package is ready]

---

## References

1. **Reasoning Bank** (Google, Sept 2025) - test-time scaling concept
2. **LangGraph Memory Paper** - episodic, semantic, procedural types
3. **ACE: Agentic Context Engineering** (Oct 2025) - procedural memory
4. **Claude Code Hooks** - [Link to hooks documentation]

For advanced implementations: Hinside article on memory (but beware local optimization trap).

---

## What's Next

- Installation package (one command install)
- Source code release (I reverse-engineered Claude Code - separate post coming)
- Autonomous team framework (where memory is the real power)

---

**Written:** 2026-01-13
**Status:** DRAFT V2 - Awaiting installation package completion
