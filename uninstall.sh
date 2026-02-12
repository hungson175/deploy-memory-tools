#!/bin/bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== Claude Code Memory System Uninstaller ===${NC}\n"

echo "This will remove:"
echo "  - Qdrant Docker container and volumes"
echo "  - Skills (coder-memory-recall, coder-memory-store)"
echo "  - Subagent (memory-only)"
echo "  - Python package"
echo ""
echo "This will NOT remove:"
echo "  - MCP config from ~/.claude.json (you'll need to do this manually)"
echo "  - .env file (in case you want to keep your API keys)"
echo "  - Project source code"
echo ""

read -p "Are you sure you want to uninstall? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstall cancelled."
    exit 0
fi

# Stop and remove Qdrant container
echo -e "${YELLOW}[1/5] Stopping Qdrant container...${NC}"
if docker ps -a --format '{{.Names}}' | grep -q "^qdrant-memory$"; then
    echo "Stopping and removing qdrant-memory container..."
    docker stop qdrant-memory 2>/dev/null || true
    docker rm qdrant-memory 2>/dev/null || true
    echo -e "${GREEN}✓ Container removed${NC}"
else
    echo "Qdrant container not found (already removed?)"
fi

# Remove Docker volume
echo "Removing Docker volume..."
docker volume rm deploy-memory-tools_qdrant_storage 2>/dev/null || echo "Volume not found or already removed"
echo -e "${GREEN}✓ Qdrant removed${NC}\n"

# Remove skills
echo -e "${YELLOW}[2/5] Removing skills...${NC}"
REMOVED_SKILLS=0

if [ -d ~/.claude/skills/coder-memory-recall ]; then
    # Backup before removing
    mv ~/.claude/skills/coder-memory-recall ~/.claude/skills/coder-memory-recall.removed.$(date +%s)
    echo "Removed coder-memory-recall (backup created)"
    REMOVED_SKILLS=$((REMOVED_SKILLS + 1))
fi

if [ -d ~/.claude/skills/coder-memory-store ]; then
    mv ~/.claude/skills/coder-memory-store ~/.claude/skills/coder-memory-store.removed.$(date +%s)
    echo "Removed coder-memory-store (backup created)"
    REMOVED_SKILLS=$((REMOVED_SKILLS + 1))
fi

if [ $REMOVED_SKILLS -gt 0 ]; then
    echo -e "${GREEN}✓ $REMOVED_SKILLS skill(s) removed${NC}\n"
else
    echo "No skills found to remove"
    echo -e "${GREEN}✓ Skills already removed${NC}\n"
fi

# Remove subagent
echo -e "${YELLOW}[3/5] Removing subagent...${NC}"
if [ -d ~/.claude/subagents/memory-only ]; then
    mv ~/.claude/subagents/memory-only ~/.claude/subagents/memory-only.removed.$(date +%s)
    echo "Removed memory-only subagent (backup created)"
    echo -e "${GREEN}✓ Subagent removed${NC}\n"
else
    echo "Subagent not found (already removed?)"
    echo -e "${GREEN}✓ Subagent already removed${NC}\n"
fi

# Remove MCP config (manual step)
echo -e "${YELLOW}[4/5] MCP configuration...${NC}"
if grep -q '"memory"' ~/.claude.json 2>/dev/null; then
    echo -e "${YELLOW}Please manually remove the 'memory' entry from ~/.claude.json${NC}"
    echo ""
    echo "Location: ~/.claude.json"
    echo "Section: mcpServers.memory"
    echo ""
    echo "Or you can run:"
    echo "  nano ~/.claude.json"
    echo ""
    echo "Config backups are available at: ~/.claude.json.backup.*"
else
    echo "No memory MCP config found in ~/.claude.json"
fi
echo ""

# Uninstall Python package
echo -e "${YELLOW}[5/5] Uninstalling Python package...${NC}"

# Check if installed
if python3 -c "import qdrant_memory_mcp" 2>/dev/null; then
    # Try to activate venv if it exists
    if [ -f .venv/bin/activate ]; then
        source .venv/bin/activate
    fi

    pip uninstall -y qdrant-memory-mcp 2>/dev/null || echo "Package not found in pip"
    echo -e "${GREEN}✓ Package uninstalled${NC}\n"
else
    echo "Package not found (already uninstalled?)"
    echo -e "${GREEN}✓ Package already uninstalled${NC}\n"
fi

# Summary
echo -e "${GREEN}=== Uninstall Complete! ===${NC}\n"

echo "What was removed:"
echo "  ✓ Qdrant Docker container and volumes"
echo "  ✓ Skills (backed up with .removed.* suffix)"
echo "  ✓ Subagent (backed up with .removed.* suffix)"
echo "  ✓ Python package"
echo ""

echo "What remains:"
echo "  - ~/.claude.json config (manual removal needed)"
echo "  - .env file (your API keys)"
echo "  - Project source code in $(pwd)"
echo "  - Virtual environment (.venv folder)"
echo ""

echo "To complete uninstallation:"
echo "  1. Edit ~/.claude.json and remove 'memory' from mcpServers"
echo "  2. Restart Claude Code"
echo "  3. Optionally: rm -rf .venv (if you don't need the dev environment)"
echo ""

echo "To reinstall later:"
echo "  ./install.sh"
