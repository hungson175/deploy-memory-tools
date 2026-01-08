# Product Backlog

## High Priority

### Memory Deduplication Service
**Added:** 2026-01-02
**Status:** Backlog

**Problem:** The Qdrant vector database accumulates duplicate memories over time, especially for roles like scrum-master. The current update mechanism exists but duplicates still creep in.

**Proposed Solution:** Create a periodic background service/script that:
- Runs on a schedule (e.g., weekly or on-demand)
- Scans each collection for semantically similar memories
- Identifies duplicates based on embedding similarity threshold
- Merges or removes duplicate entries
- Logs cleanup actions for audit

**Notes:**
- Implementation details TBD
- Consider: similarity threshold, merge strategy, dry-run mode
- Could be a cron job or manual trigger

---

## Medium Priority

(none yet)

---

## Low Priority

(none yet)

---

## Completed

(none yet)
