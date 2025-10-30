# Crontab Setup for Automatic Memory Sync

## Overview

The memory vector database (Qdrant) is automatically synced from the source of truth (files) every Monday at 11AM using a crontab job.

## Setup Instructions

Run this command to add the crontab entry:

```bash
(crontab -l 2>/dev/null; echo "# Sync memory vectors every Monday at 11AM"; echo "0 11 * * 1 /Users/sonph36/dev/deploy-memory-tools/sync_memories.sh >> /Users/sonph36/dev/deploy-memory-tools/sync.log 2>&1") | crontab -
```

## Verify Installation

Check that the crontab entry was added:

```bash
crontab -l
```

You should see:
```
# Sync memory vectors every Monday at 11AM
0 11 * * 1 /Users/sonph36/dev/deploy-memory-tools/sync_memories.sh >> /Users/sonph36/dev/deploy-memory-tools/sync.log 2>&1
```

## Manual Sync

To manually trigger a sync at any time:

```bash
cd /Users/sonph36/dev/deploy-memory-tools
./sync_memories.sh
```

## Check Sync Logs

View sync history:

```bash
tail -50 /Users/sonph36/dev/deploy-memory-tools/sync.log
```

## How It Works

1. **Crontab schedule**: `0 11 * * 1` = Every Monday at 11:00 AM
2. **Wrapper script**: `sync_memories.sh` changes to project directory and runs migration
3. **Migration script**: `migrate_memories.py` recreates vector database from file-based memories
4. **Logs**: Output redirected to `sync.log` for troubleshooting

## Remove Crontab Entry

If you want to remove the automatic sync:

```bash
crontab -l | grep -v "sync_memories.sh" | crontab -
```
