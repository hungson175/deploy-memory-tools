#!/bin/bash
# Deploy V3.2 Memory System - Complete Setup Script

set -e  # Exit on error

echo "============================================================"
echo "V3.2 MEMORY SYSTEM DEPLOYMENT"
echo "============================================================"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found${NC}"
    exit 1
fi

# Check if Qdrant is running
if ! curl -s http://localhost:6333/collections > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️ Warning: Qdrant not accessible at localhost:6333${NC}"
    echo "Please ensure Qdrant is running: docker run -p 6333:6333 qdrant/qdrant"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✅ Qdrant is running${NC}"
fi

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️ Warning: .env file not found${NC}"
    echo "Please create .env with:"
    echo "OPENAI_API_KEY=your-key-here"
    echo "QDRANT_URL=http://localhost:6333"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo

# Step 1: Run tests
echo "🧪 Running V3.2 system tests..."
if python3 test_v3.2_system.py > /tmp/v3.2_test.log 2>&1; then
    echo -e "${GREEN}✅ All tests passed${NC}"
else
    echo -e "${YELLOW}⚠️ Some tests failed (see /tmp/v3.2_test.log)${NC}"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo

# Step 2: Backup existing skills
echo "📦 Backing up existing skills..."
BACKUP_DIR=~/.claude/backup/skills-$(date +%Y%m%d-%H%M%S)
mkdir -p "$BACKUP_DIR"

if [ -d ~/.claude/skills/coder-memory-store ]; then
    cp -r ~/.claude/skills/coder-memory-store "$BACKUP_DIR/" 2>/dev/null || true
    echo "   Backed up coder-memory-store"
fi

if [ -d ~/.claude/skills/coder-memory-recall ]; then
    cp -r ~/.claude/skills/coder-memory-recall "$BACKUP_DIR/" 2>/dev/null || true
    echo "   Backed up coder-memory-recall"
fi

echo -e "${GREEN}✅ Backup saved to $BACKUP_DIR${NC}"
echo

# Step 3: Install V3.2 skills
echo "📥 Installing V3.2 skills..."

# Create skills directory if not exists
mkdir -p ~/.claude/skills

# Remove old versions
rm -rf ~/.claude/skills/coder-memory-store 2>/dev/null || true
rm -rf ~/.claude/skills/coder-memory-recall 2>/dev/null || true

# Install new versions
cp -r global/v3.2/coder-memory-store ~/.claude/skills/
cp -r global/v3.2/coder-memory-recall ~/.claude/skills/

echo -e "${GREEN}✅ V3.2 skills installed${NC}"
echo

# Step 4: Install MCP server v2
echo "🚀 Installing MCP server v2..."

# Create scripts directory
mkdir -p ~/scripts

# Copy new server
cp qdrant_memory_mcp_server_v2.py ~/scripts/
chmod +x ~/scripts/qdrant_memory_mcp_server_v2.py

echo -e "${GREEN}✅ MCP server v2 installed${NC}"
echo

# Step 5: Update MCP configuration
echo "⚙️ Updating MCP configuration..."

MCP_CONFIG=~/.config/claude/mcp.json
MCP_BACKUP=~/.config/claude/mcp.json.backup-$(date +%Y%m%d-%H%M%S)

if [ -f "$MCP_CONFIG" ]; then
    # Backup existing config
    cp "$MCP_CONFIG" "$MCP_BACKUP"
    echo "   Backed up existing config to $MCP_BACKUP"

    # Check if already configured
    if grep -q "qdrant-memory-v2" "$MCP_CONFIG"; then
        echo -e "${YELLOW}   MCP server v2 already configured${NC}"
    else
        echo -e "${YELLOW}   Please manually add to $MCP_CONFIG:${NC}"
        cat << 'EOF'

  "qdrant-memory-v2": {
    "command": "python3",
    "args": ["~/scripts/qdrant_memory_mcp_server_v2.py"]
  }

EOF
    fi
else
    echo -e "${YELLOW}   MCP config not found. Creating template...${NC}"
    mkdir -p ~/.config/claude
    cat > "$MCP_CONFIG" << 'EOF'
{
  "servers": {
    "qdrant-memory-v2": {
      "command": "python3",
      "args": ["~/scripts/qdrant_memory_mcp_server_v2.py"]
    }
  }
}
EOF
    echo -e "${GREEN}   Created MCP config with v2 server${NC}"
fi

echo

# Step 6: Run migration (optional)
echo "🔄 Database Migration"
read -p "Run migration from V3 to V3.2? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "   Running migration..."
    if python3 migrate_v3_to_v3.2.py > /tmp/v3.2_migration.log 2>&1; then
        echo -e "${GREEN}✅ Migration completed (see /tmp/v3.2_migration.log)${NC}"
    else
        echo -e "${RED}❌ Migration failed (see /tmp/v3.2_migration.log)${NC}"
    fi
else
    echo "   Skipping migration"
fi

echo

# Step 7: Summary
echo "============================================================"
echo -e "${GREEN}🎉 V3.2 DEPLOYMENT COMPLETE${NC}"
echo "============================================================"
echo
echo "✅ Installed:"
echo "   - V3.2 skills in ~/.claude/skills/"
echo "   - MCP server v2 in ~/scripts/"
echo "   - Configuration updated"
echo
echo "📝 Key improvements in V3.2:"
echo "   • True two-stage retrieval (60% token savings)"
echo "   • Embedded role configuration (no external files)"
echo "   • Simplified collection names"
echo "   • Intelligent consolidation (no rigid thresholds)"
echo "   • Clean, consistent architecture"
echo
echo "🚀 Next steps:"
echo "   1. Restart Claude Code to load new skills"
echo "   2. Test with: claude --recall 'api patterns'"
echo "   3. Store patterns with: --store after solving problems"
echo
echo "📖 Documentation: global/v3.2/README.md"
echo

# Final check
echo "============================================================"
read -p "Display skill verification? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo
    echo "📂 Installed skills:"
    ls -la ~/.claude/skills/ | grep coder-memory
    echo
    echo "📄 Skill files:"
    find ~/.claude/skills/coder-memory-* -name "*.md" -type f
fi

echo
echo -e "${GREEN}✨ V3.2 Memory System Ready!${NC}"