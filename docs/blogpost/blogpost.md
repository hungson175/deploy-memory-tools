# Memory for Claude Code: A Practical Guide

**DRAFT v1**

---

## The Problem

Claude Code is like a top student going to an international competition - extremely smart and talented, but forgets all the knowledge from the previous day every day, and repeats the same bugs from before. So it doesn't accomplish much. Not very useful.

**Memory solves that problem.**

---

## Three Questions for Memory Systems

Building memory for coding agents comes down to answering three questions: **How, What, When**.

Most people think about them in that order. But in practice, **"when" is the hardest** - and almost no paper addresses it.

---

### 1. How: Storage Mechanism

**Short answer:** Use files + vector database. That's it.

People love to argue about page indexes, tree structures, knowledge graphs, whatever. **Who cares?** Differences of 10-20% don't matter when next year Google releases something and it all flies away anyway.

Don't waste time on this. Just pick something that works.

---

### 2. What: Content to Store

This is where it gets interesting.

The only valuable insight from Google's Reasoning Bank paper (Sept 2025): **"Memory is test-time scaling."**

Think about it - you have a very smart AI, but it has amnesia. Forgets everything daily. Attach memory to it, let it run in the environment, and it self-learns through interactions.

**Coding agents are PERFECT for this:**
- Completely digital environment
- Built-in feedback mechanisms
- Can improve gradually over time

#### Three Types of Memory

From the LangGraph memory paper:

**1. Episodic (Specific + TTL)**
- Concrete events: "Binance API has 500 req/min rate limit"
- **Must have TTL** - memory dies after a while
- Prevents outdated specifics from polluting your database

**2. Semantic (Generalized)**
- Universal patterns: "External APIs require rate limit consideration"
- Extracted from episodic experiences
- Stays relevant across contexts

**3. Procedural (Workflows)**
- Team processes: "When integrating external API, check rate limits first in docs"
- Critical for self-improvement
- See ACE: Agentic Context Engineering (Oct 2025) for elegant implementation

**Example flow:**
1. Hit Binance API rate limit (specific bug)
2. Store episodic memory with TTL
3. Extract semantic pattern (check rate limits)
4. Update procedural workflow (integration checklist)

**Why generalization matters:** If you just store "Binance rate limit = 500/min", three days later that file might change. Your memory is now garbage. Generalize or die.

---

### 3. When: Trigger Conditions

**This is the hardest question.** Two parts:

#### When to STORE?

**Simple:** After the while loop completes.

Claude Code runs in a while loop (~10 lines of code). When the task finishes, ask: "Anything worth storing?" Full context is still there. No fear of losing anything.

Optional: Use random sampling (I use 1/3 chance) to reduce noise.

#### When to RETRIEVE?

**The clever solution:** Hook on the planning tool.

Claude Code has a planning tool (`TodoWrite`) that it calls when starting complex tasks. That's your trigger.

**Why this is brilliant:**
1. **Selective** - Only complex tasks trigger retrieval (simple tasks skip it)
2. **Context-aware** - Agent already knows what it needs to do when it plans
3. **Perfect timing** - Right when it outlines "I need to research X, implement Y, test Z"

That's exactly when you want to retrieve past memories related to the task.

**Implementation:** Use Claude Code's hooks system. Hook on `TodoWrite` post-tool-use. Done.

---

## Summary

| Question | Answer |
|----------|--------|
| **How** | Files + Vector DB (don't overthink it) |
| **What** | Episodic (TTL) + Semantic (generalized) + Procedural (workflows) |
| **When (Store)** | After while loop completes |
| **When (Retrieve)** | When planning tool is called |

---

## My Implementation

I've implemented this memory system using:
- Qdrant vector database
- MCP server for Claude Code integration
- Role-based collections (backend, frontend, AI, etc.)
- Two-stage retrieval (previews first, full content on demand)

The architecture is simple. No fancy stuff. It works.

**Coming soon:**
- One-command installation
- Complete with MCP server, Docker/Qdrant, skills, and subagents
- Practical examples and usage guide

---

## Don't Over-Engineer

**Final note:** Memory is THE hot topic (end 2025 → biggest keyword 2026). Anthropic already has memory in their beta header. Google has papers on nested architecture solving memory at the LLM level.

**My advice:** Implement something simple that works. Don't spend months optimizing. Sooner or later, Google/Anthropic/OpenAI will release memory at the model layer, and all our external engineering will fly away anyway.

Dividing by zero gives infinity, but 1/2 vs 1/3 (23% difference)? Doesn't solve anything.

**If there's memory, coding agents will be completely different.** But don't waste time over-engineering - the big players are already on it.

---

## References

1. **Reasoning Bank** (Google, Sept 2025) - test-time scaling concept
2. **LangGraph Memory Paper** - episodic, semantic, procedural types
3. **ACE: Agentic Context Engineering** (Oct 2025) - procedural memory

For fancy implementations, see the Hinside article on memory - but remember: local optimization trap. Keep it simple.

---

## What's Next

I'm working on making this memory system easily installable for Claude Code. When it's ready, I'll share:
- Installation package (one command, everything works)
- Source code (I reverse-engineered Claude Code - separate blog post coming)
- Autonomous team framework (where memory is the real power, not the fancy UI)

Stay tuned.

---

**Written:** 2026-01-13
**Status:** DRAFT - Awaiting complete installation package before public release
