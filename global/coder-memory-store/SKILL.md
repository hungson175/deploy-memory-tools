---
name: Coder Memory Store
description: Store universal coding patterns and insights into file-based memory. Use after completing difficult tasks with broadly-applicable lessons that work across ANY project. Use when user says "--coder-store" or "--learn" (you decide which scope, may use both) or after discovering framework-agnostic patterns. ALSO invoke when user expresses strong frustration using trigger words like "fuck", "fucking", "shit", "moron", "idiot", "stupid", "garbage", "useless", "terrible", "wtf", "this is ridiculous", "you're not listening" - these are CRITICAL learning signals for storing failure patterns. Skip for routine work or project-specific details (use project-memory-store).
---


**Purpose**: Extract and store **universal coding patterns** (episodic/procedural/semantic) into file-based memory at `~/.claude/skills/coder-memory-store/`.

**Key Architecture**: This SKILL.md + subdirectory README.md files form a **tree guideline structure** for progressive disclosure - overview at top, details deeper. This is very effective for information retrieval.

**Keep SKILL.md lean**: Provide overview and reference other files. When this file becomes unwieldy, split content into separate files and reference them. Trust Claude to read detailed files only when needed.

**When to Use**:
- After solving non-obvious bugs with broadly-applicable solutions
- When discovering universal patterns (debugging strategies, architectural insights, framework-agnostic techniques)
- User explicitly says "--coder-store" or "--learn" (Claude decides if universal or project-specific, may use both)
- Completed difficult tasks with lessons ANY coding project could benefit from

**CRITICAL**: Store BOTH successful AND failed trajectories. Failures are equally important - often MORE valuable than successes. Failed approaches teach what NOT to do and why.

**When NOT to Use**:
- Routine tasks or standard debugging
- Project-specific configurations or architecture decisions (use project-memory-store)
- Obvious or well-known patterns

**Selection Criteria**: Most conversations yield 0-1 universal insights. Be highly selective.

---

## PHASE 0: Initialize Memory Structure

Check if memory directories exist at `~/.claude/skills/coder-memory-store/`:
- `episodic/` - Concrete coding events with full context
- `procedural/` - Proven workflows and how-to steps
- `semantic/` - Distilled principles and patterns

If missing, create directories and initialize each with single file:
- `episodic/episodic.md`
- `procedural/procedural.md`
- `semantic/semantic.md`

Update `SKILL.md` (this file) as needed when structure changes - modify ANY part to keep it accurate and useful.

---

## PHASE 1: Extract Insights

Analyze conversation and extract **0-3 insights** (most yield 0-1).

**Classify each as**:
- **Episodic**: Concrete events (debugging session, implementation story) with full context
- **Procedural**: Repeatable workflow or step-by-step process
- **Semantic**: General principle or pattern (abstracted from experience)

**Extraction Criteria** (ALL must be true):
1. **Non-obvious**: Not standard practice or well-documented
2. **Universal**: Applies across multiple projects/languages/frameworks
3. **Actionable**: Provides concrete guidance for future situations
4. **Generalizable**: Can be abstracted beyond specific codebase

**Reject**:
- Project-specific details (use project-memory-store)
- Routine work or obvious patterns
- Standard practices already well-known

---

## PHASE 2: Search for Similar Memories

For each extracted insight:

**Step 1: Determine target memory type** (episodic/procedural/semantic)

**Step 2: Search existing files**
- Use Grep to search for keywords across memory files
- Search in target memory type directory (e.g., `~/.claude/skills/coder-memory-store/episodic/`)
- Look for similar titles, tags, or core concepts
- Read files with potential matches

**Step 3: Check similarity**
- If found similar content: Read full context
- Determine if: Duplicate, Related, or Different

---

## PHASE 3: Consolidation Decision

**Decision Matrix** (file-based consolidation):

| Similarity | Action | Rationale |
|-----------|--------|-----------|
| **Duplicate/Very Similar** | **MERGE** | Combine into single stronger entry |
| **Related (same topic)** | **UPDATER** | Update existing memory with new information |
| **Pattern Emerges** | **GENERALIZE** | Extract pattern → promote episodic to semantic |
| **Different** | **CREATE** | New file or separate section |

**Actions**:

**MERGE** (duplicate or very similar):
- Combine both memories into single, stronger entry
- Eliminate redundancy, keep unique details from both
- If contradictory: Add "**Previous Approach:**" and tag #reconsolidated
- Update in existing file

**UPDATER** (related, same topic):
- Update existing memory with new information
- If extends existing: Add new details inline with note "**Updated [date]:**"
- If alternative approach: Add separate entry in same file with cross-reference
- If contradicts: Add "**Previous approach:**" to show evolution of understanding

**GENERALIZE** (pattern emerges from multiple episodic memories):
- Extract common pattern from 2+ similar episodic entries
- Create/update semantic memory with the generalized pattern
- Reference episodic examples in semantic entry
- Tag episodic entries with reference to semantic pattern
- This is how learning happens: specific experiences → general principles

**CREATE** (different topic):
- Store in new location (new file or different section)
- Update README.md to reference new content

---

## PHASE 4: Store Memory

**CRITICAL: Use COMPACT format to prevent memory bloat. Each memory = 3-5 sentences MAX.**

**Universal Format** (works for ALL memory types):
```
**Title:** <concise title>
**Description:** <one sentence summary>

**Content:** <3-5 sentences covering: what happened, what was tried (including failures), what worked/failed, key lesson>

**Tags:** #tag1 #tag2 #success OR #failure
```

**Formatting Rules**:
- NO blank line between Title and Description
- ONE blank line before Content
- ONE blank line before Tags
- Content MUST be 3-5 sentences (not paragraphs, not lists, not verbose sections)
- Include both failures and successes in Content if relevant
- Tag episodic memories with #episodic, procedural with #procedural, semantic with #semantic

**Determine storage location**:
1. **Read README.md** (if exists) in target memory type directory
2. **Decide based on consolidation action**:
   - MERGE/UPDATER: Modify existing file
   - GENERALIZE: Update semantic/ or create new semantic file
   - CREATE: New file or new section
3. **Max depth**: 2 levels (e.g., `semantic/error-handling/` is deepest)

**Execute storage**:
1. Write formatted memory to file (merge, update, append, or create)
2. If file becomes "too long" with unrelated info:
   - Create subdirectory with topic name
   - Move related memories to new file in subdirectory
   - Create README.md in subdirectory as overview
3. Update parent README.md to reference new structure

---

## PHASE 5: Update Skill Metadata

If directory structure changed (new subdirectories created):
- Update this SKILL.md frontmatter `description` if needed
- Ensure future recalls can discover new structure

---

## Final Report

**Format**:
```
✅ Coder Memory Storage Complete

**Insights Extracted**: <number> universal patterns
  - Episodic: <number>
  - Procedural: <number>
  - Semantic: <number>

**Storage Actions**:
  - Appended to existing files: <number>
  - Created new files/subdirectories: <number>

**Quality Check**:
  - ✓ All insights are universal (framework/project-agnostic)
  - ✓ All insights are non-obvious
  - ✓ File organization maintained (max 2-level depth)
```

**If 0 insights extracted**:
```
✅ Coder Memory Storage Complete

**Insights Extracted**: 0 (conversation contained routine work or project-specific details)

Consider using project-memory-store for project-specific insights.
```

---

## Self-Maintenance Note

This skill's memory files can be refactored by coder-memory-recall when organization becomes unclear. The recall skill will invoke general-purpose agent to reorganize structure if needed.
