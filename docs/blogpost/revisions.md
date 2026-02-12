# Blog Post Revisions & Feedback

**Draft:** v1 → v2 → v3 (upcoming)
**Date:** 2026-01-13

---

## V2 Review Feedback (Preparing for V3)

### ✅ What's Good in V2
- Problem section: extremely satisfied
- Solution section: extremely satisfied
- "How it works (Optional)" break: great
- Overall structure: working well

---

### 🔴 CRITICAL ISSUE: Missing Practical Application

**Problem:** V2 explains theory but doesn't show HOW WE APPLY IT IN CLAUDE CODE

**For V3:** Each section (How, What, When) needs TWO parts:
1. **Theory** - Brief explanation from papers
2. **Our Application** - How we modified/applied it in Claude Code

**Example structure:**
```
## 1. How: Storage Mechanism

### Theory (from papers)
[Brief explanation]

### How We Apply It in Claude Code
[Our specific implementation]
```

**Without practical application, it's just useless theory.**

This needs to be fixed clearly in V3.

---

### References Section (for "How: Storage Mechanism")

**Add at end of How section:**

**References:**

*Papers we use:*
- **ACE: Agentic Context Engineering** (Oct 2025) - [our implementation uses this]
- **Reasoning Bank** (Google, Sept 2025) - test-time scaling
- **LangChain Agent Memory Paper** - episodic, semantic, procedural

*Other approaches (work but I don't care):*
- Page Index - [link to be added]
- Knowledge Graph - [link to be added]
- Hinside article on memory

**Note:** Don't use word "Fancy" - just say "work but I don't care" or similar straightforward language.

---

### Episodic Memory Addition

**Add to Episodic explanation:**

Before episodic memory dies (TTL expires), try to extract it into semantic (general) memory.

**But note:** Once extracted to semantic, it's already stored. So when episodic dies later, no problem - the valuable pattern is preserved.

**Flow:**
1. Store episodic with TTL
2. Extract semantic pattern (happens early)
3. Episodic eventually dies (that's fine)
4. Semantic stays forever

---

## V1 → V2 Changes (Completed)

### Structure Change: Problem → Solution → Explanation (Optional)

**Target audience:** Practical users who want to use it ASAP, don't need to understand everything

**Reading flow:**
1. **Problem** - Quick, concise (made shorter than v1) ✅
2. **Solution** - Brief: package available, installable, link at end ✅
3. **Explanation** (optional) - Deep dive for those who want to understand ✅

---

### Specific Changes Made

**1. Problem Section** ✅
Shortened from v1 while keeping punch:
> "Claude Code is brilliant but has amnesia - forgets everything daily, repeats the same bugs. Not very useful."

**2. Solution Section Added** ✅
- States package exists and is installable
- References installation link at end
- SHORT - just enough to know it exists

**3. "What" Section Rewritten** ✅
- First sentence: storing every memory = garbage + not useful
- Example flow made clearer:
  - Point 1: Hit Binance API, locked hours
  - Point 2: Store episodic "1200 req/min, see binance_crawler.py"
  - Point 3: Extract semantic "check rate limits"
  - Point 4: REMOVED (procedural is special)

**4. "When" Section** ✅
- Added reference to hooks documentation at end

**5. "How" Section** ✅
- Kept as-is (satisfactory)

---

## Audience Segmentation

**Primary audience (80%):**
- Just want to use it
- Don't care about theory
- Need: Problem → Solution → Install link

**Secondary audience (20%):**
- Curious about how it works
- Want to understand the architecture
- Will read the explanation section

**Write for primary, provide optional content for secondary**

---

## Next Steps for V3

- [ ] Add "Theory vs Our Application" structure to each section (How, What, When)
- [ ] Add References section to "How: Storage Mechanism"
- [ ] Add episodic→semantic extraction note to "What" section
- [ ] Ensure each section clearly shows PRACTICAL implementation in Claude Code
- [ ] Fill in paper links when available

---

**Status:** V2 complete, awaiting V3 revisions based on review feedback
