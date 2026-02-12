# Product Backlog - Memory MCP Server

**Owner**: PO
**Purpose**: Prioritized list of all work items

**Note**: This backlog is managed by PO. Main project backlog is in docs/BACKLOG.md. This file tracks current sprint work.

---

## P0 - Critical (Blocks Public Release)

- [ ] Architecture Review: Verify v3.2 implementation matches draft_v7.md blog post
  - Create docs/architecture_review.md
  - Compare MCP server implementation with blog descriptions
  - Document actual vs. described architecture

- [ ] Easy Installation Package
  - One-command installation (./install.sh or npm/pip)
  - Auto-configure MCP server + Docker + Skills + Subagents
  - Zero manual configuration required

- [ ] Code Review & Quality Check
  - Remove dead/duplicate code
  - Clean up commented sections
  - Proper error handling
  - Professional naming and structure

---

## P1 - Major (Next Tasks)

- [ ] Blog Post: Memory Architecture for Coding Agents
  - Requires installation package first
  - Include sample implementation
  - Open source repository link

---

## P2 - Nice to Have (When Time Allows)

- [ ] Fix 9 bugs from LOG_BUGES.md
  - BUG #2: Add "qa" role to ROLE_COLLECTIONS (5 min)
  - BUG #1: Migrate universal-patterns to flat structure (30 min)
  - BUG #4: Ensure all items have description field
  - BUG #3: Delete duplicate coder-memory collection
  - See LOG_BUGES.md for complete list

---

## P3 - Future Ideas (Low Priority)

- [ ] Documentation updates (CLAUDE.md, architecture docs)
- [ ] Examples of episodic/semantic/procedural memory usage

---

## Done

(None yet)

---

**Notes**:
- PO owns this file - update directly when Boss provides feedback
- Auto-add Boss feedback to appropriate priority level
- Move items to "Done" after Boss accepts work
- Reference main project backlog at docs/BACKLOG.md for full details

**Last Updated**: 2026-01-16 by PO
