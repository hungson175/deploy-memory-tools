#!/bin/bash
# Wrapper script for crontab to sync memory vectors
cd /Users/sonph36/dev/deploy-memory-tools

echo "=== Memory Vector Sync Started at $(date) ==="

# Delete existing collection
echo "Deleting existing collection..."
curl -X DELETE http://localhost:6333/collections/coder-memory 2>&1

# Recreate collection
echo "Recreating collection..."
curl -X PUT 'http://localhost:6333/collections/coder-memory' \
  -H 'Content-Type: application/json' \
  -d '{"vectors":{"size":1536,"distance":"Cosine"}}' 2>&1

# Migrate memories
echo "Migrating memories..."
/Library/Frameworks/Python.framework/Versions/3.11/bin/python3 migrate_memories.py

echo "=== Memory Vector Sync Completed at $(date) ==="
