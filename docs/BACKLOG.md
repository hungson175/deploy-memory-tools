# Project Backlog

## Critical Priority (P0)

### Architecture Review: Blog Post vs Implementation Alignment
**Status:** Not Started
**Priority:** P0 - CRITICAL (Blocks public release)
**Description:** Review memory system architecture (v3.2) and verify it matches what's described in draft_v7.md blog post. Ensure consistency between documentation and actual implementation before packaging and publishing.

**Review scope:**
1. Current architecture (src/qdrant_memory_mcp v3.2)
2. Compare with draft_v7.md descriptions
3. Identify mismatches or inconsistencies
4. Document actual architecture in docs/architecture_review.md

**Questions to answer:**
- Does the MCP server implementation match blog description?
- Are the memory types (episodic/semantic/procedural) implemented as described?
- Does two-stage retrieval work as documented?
- Are role-based collections accurate?
- Do hooks and skills exist as described?

**Output:** Architecture review document in docs/architecture_review.md

**Dependencies:**
- Blocks: Blog post finalization (must be consistent)
- Blocks: Installation package creation (need clean architecture first)

---

### Make Memory System Easily Installable for Claude Code
**Status:** Not Started
**Priority:** P0 - CRITICAL (Blocks blog post public release)
**Description:** Create complete one-click installation package for memory system. When user installs, EVERYTHING should work immediately.

**Complete package must include:**
1. **MCP Server** - The memory server itself
2. **Docker/Qdrant Setup** - Automated Qdrant container startup
3. **Skills** - Auto-install coder-memory-recall and coder-memory-store
4. **Subagents** - Auto-install memory-only subagent
5. **Configuration** - Automated `~/.claude.json` setup
6. **Environment** - API keys setup (OpenAI/Voyage)

**User experience goal:**
```bash
# User runs ONE command
./install.sh
# OR
npm install -g claude-code-memory
# OR
pip install claude-code-memory

# Everything auto-configures and works immediately
```

**Blockers for public release:**
- Need one-command installation process
- Users should not need deep technical knowledge
- Must work out-of-the-box with Claude Code
- No manual configuration required

**Installation script must:**
- Check dependencies (Docker, Python, etc.)
- Start Qdrant container automatically
- Install MCP server
- Copy skills to `~/.claude/skills/`
- Copy subagent to `~/.claude/agents/`
- Update `~/.claude.json` with MCP config
- Prompt for API keys and save to .env
- Verify everything works
- Print success message with next steps

**Research needed:**
- How other MCP servers distribute/install (check popular ones)
- Claude Code MCP server installation best practices
- Package managers (npm, pip, uv, etc.)
- Docker Compose for bundling
- Skills/subagents installation mechanism

**Deliverables:**
1. Complete installation script/package
2. Clear README with one-command install
3. Automated Docker Compose setup
4. Skills + subagents auto-installation
5. Configuration automation for `~/.claude.json`
6. Verification/testing script
7. Troubleshooting guide
8. Uninstall script

**Dependencies:**
- Blocks: Blog post public release (can't publish without easy install)
- Requires: Bug fixes + code review completed (clean working system first)

---

### Code Review & Quality Check Before Public Release
**Status:** Not Started
**Priority:** P0 - CRITICAL (Blocks public release)
**Description:** Thoroughly review and polish the memory system and MCP server before making it public. Cannot release half-assed embarrassing code.

**Review areas:**
1. **Code quality**
   - Remove dead/duplicate code
   - Clean up commented-out sections
   - Proper error handling
   - Consistent style and formatting

2. **Architecture review**
   - Is the design clean and understandable?
   - Are there architectural flaws or embarrassing hacks?
   - Is it maintainable?

3. **Documentation**
   - Clear README for public consumption
   - Code comments where needed
   - API documentation
   - Examples and usage guides

4. **Testing**
   - Does it actually work end-to-end?
   - Edge cases handled?
   - Error messages helpful?

5. **Polish**
   - Remove debug logging/prints
   - Clean up file structure
   - Remove backup/temp files
   - Professional naming conventions

**Quality gate:**
- Would I be proud to show this to other developers?
- Is it embarrassing? If yes, FIX IT.
- Does it represent professional work?

**Dependencies:**
- Blocks: Blog post public release
- Blocks: Easy installation task (need clean code first)
- Requires: Bug fixes from LOG_BUGES.md

---

## High Priority (P1)

### Write Blog Post: Memory Architecture for Coding Agents
**Status:** Ideas captured in `blog-post-ideas.md`
**Priority:** P1 - High
**Dependencies:** Requires easy installation method (P0 task above)
**Description:** Write blog post about memory implementation for coding agents based on:
- Three questions framework: How, What, When
- Reasoning Bank paper (test-time scaling)
- LangGraph memory types (episodic, semantic, procedural)
- ACE paper (procedural memory)
- Claude Code architecture insights

**Key points:**
- Don't over-engineer - big companies solving at model level
- Memory is test-time scaling
- Hook on TodoWrite for retrieval timing
- Store after while loop completion

**Deliverables:**
1. Blog post draft
2. Sample memory implementation for Claude Code integration ⚠️ **MOST IMPORTANT**
3. Open source code repository link
4. Teaser for autonomous team framework

**References needed:**
- Reasoning Bank (Google, Sept 2025)
- LangGraph memory paper
- ACE: Agentic Context Engineering (Oct 2025)
- Hinside article on memory
- Anthropic articles

---

## Medium Priority (P2)

### Fix Memory System Bugs
**Status:** Documented in `LOG_BUGES.md`
**Priority:** P2 - Medium
**Description:** Fix 9 bugs in memory system identified during debugging session

**Critical bugs (P0-P1):**
1. BUG #2: Add "qa" role to ROLE_COLLECTIONS (5 min) ⚡
2. BUG #1: Migrate universal-patterns to flat structure (30 min)
3. BUG #4: Ensure all items have description field
4. BUG #3: Delete duplicate coder-memory collection

**See `LOG_BUGES.md` for complete list and fix order**

---

## Low Priority (P3)

### Documentation Updates
- [ ] Update CLAUDE.md with memory_level removal
- [ ] Document new role-based architecture
- [ ] Add examples of episodic/semantic/procedural memory usage

---

## Ideas / Future

### Autonomous Software Team Framework
**Status:** Concept
**Description:** Framework for entire software team to work autonomously
- Fancy UI (but not the important part)
- **Memory is the real power** - emphasize this
- Integration with Claude Code
- Team specialization (frontend, backend, AI, etc.)

### Claude Code Reverse Engineering Blog Post
**Status:** Planned
**Description:** Separate blog post about reverse engineering Claude Code
- How I built SPH Code
- Architecture insights (just a while loop)
- Prompting techniques
- Open source code release

---

**Last updated:** 2026-01-13
