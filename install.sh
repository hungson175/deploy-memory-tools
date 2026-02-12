#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Claude Code Memory System Installer ===${NC}\n"

# Step 1: Check dependencies
echo -e "${YELLOW}[1/10] Checking dependencies...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed. Please install Docker first.${NC}"
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker.${NC}"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]; }; then
    echo -e "${RED}Error: Python 3.10+ required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker: Running${NC}"
echo -e "${GREEN}✓ Python: $PYTHON_VERSION${NC}\n"

# Step 2: Install Python package
echo -e "${YELLOW}[2/10] Installing Python package...${NC}"

# Create venv if it doesn't exist
if [ ! -d .venv ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate venv and install
source .venv/bin/activate

if command -v uv &> /dev/null; then
    echo "Using uv for installation..."
    uv pip install -e ".[dev]"
else
    echo "Using pip for installation..."
    pip install -e ".[dev]"
fi

echo -e "${GREEN}✓ Package installed${NC}\n"

# Step 3: Start Qdrant container
echo -e "${YELLOW}[3/10] Starting Qdrant container...${NC}"

# Check if container exists
if docker ps -a --format '{{.Names}}' | grep -q "^qdrant-memory$"; then
    echo "Qdrant container already exists. Checking status..."
    if docker ps --format '{{.Names}}' | grep -q "^qdrant-memory$"; then
        echo "Qdrant is already running."
    else
        echo "Starting existing Qdrant container..."
        docker start qdrant-memory
    fi
else
    echo "Creating new Qdrant container..."
    docker-compose up -d
fi

# Wait for Qdrant to be ready
echo "Waiting for Qdrant to start..."
for i in {1..30}; do
    if curl -s http://localhost:6333/healthz > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Qdrant is running${NC}\n"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}Warning: Qdrant health check timeout. Check Docker logs.${NC}"
        echo "Run: docker logs qdrant-memory"
        echo ""
    fi
    sleep 1
done

# Step 4: Install skills
echo -e "${YELLOW}[4/10] Installing skills...${NC}"
mkdir -p ~/.claude/skills

# Check if skills exist in current directory
if [ ! -d "skills/coder-memory-recall" ] && [ ! -d "~/.claude/skills/coder-memory-recall" ]; then
    echo -e "${YELLOW}Warning: Skills not found in project directory. Checking ~/.claude/skills...${NC}"
fi

# Try to copy from project skills directory first
if [ -d "skills/coder-memory-recall" ]; then
    # Backup existing
    if [ -d ~/.claude/skills/coder-memory-recall ]; then
        echo "Backing up existing coder-memory-recall..."
        mv ~/.claude/skills/coder-memory-recall ~/.claude/skills/coder-memory-recall.backup.$(date +%s)
    fi
    cp -r skills/coder-memory-recall ~/.claude/skills/
    echo "Installed coder-memory-recall"
fi

if [ -d "skills/coder-memory-store" ]; then
    # Backup existing
    if [ -d ~/.claude/skills/coder-memory-store ]; then
        echo "Backing up existing coder-memory-store..."
        mv ~/.claude/skills/coder-memory-store ~/.claude/skills/coder-memory-store.backup.$(date +%s)
    fi
    cp -r skills/coder-memory-store ~/.claude/skills/
    echo "Installed coder-memory-store"
fi

# If not found in project, they might already be in ~/.claude/skills
if [ -d ~/.claude/skills/coder-memory-recall ] && [ -d ~/.claude/skills/coder-memory-store ]; then
    echo -e "${GREEN}✓ Skills installed${NC}\n"
else
    echo -e "${YELLOW}⚠ Skills not found. They should be in ~/.claude/skills/ already.${NC}\n"
fi

# Step 5: Install memory-only subagent
echo -e "${YELLOW}[5/10] Installing memory-only subagent...${NC}"
mkdir -p ~/.claude/subagents

if [ ! -f "subagents/memory-only/AGENT.md" ]; then
    echo -e "${YELLOW}Warning: subagents/memory-only/AGENT.md not found. Skipping subagent installation.${NC}"
    echo "You may need to create this manually or it may already exist at ~/.claude/subagents/"
else
    if [ -d ~/.claude/subagents/memory-only ]; then
        echo "Backing up existing memory-only subagent..."
        mv ~/.claude/subagents/memory-only ~/.claude/subagents/memory-only.backup.$(date +%s)
    fi
    cp -r subagents/memory-only ~/.claude/subagents/
    echo -e "${GREEN}✓ Subagent installed${NC}\n"
fi

# Step 6: Install hooks
echo -e "${YELLOW}[6/10] Installing hooks...${NC}"
mkdir -p ~/.claude/hooks

# Install todowrite_memory_recall.py
if [ -f "hooks/todowrite_memory_recall.py" ]; then
    if [ -f ~/.claude/hooks/todowrite_memory_recall.py ]; then
        echo "Backing up existing todowrite_memory_recall.py..."
        mv ~/.claude/hooks/todowrite_memory_recall.py ~/.claude/hooks/todowrite_memory_recall.py.backup.$(date +%s)
    fi
    cp hooks/todowrite_memory_recall.py ~/.claude/hooks/
    chmod +x ~/.claude/hooks/todowrite_memory_recall.py
    echo "Installed todowrite_memory_recall.py"
fi

# Install memory_store_reminder.py
if [ -f "hooks/memory_store_reminder.py" ]; then
    if [ -f ~/.claude/hooks/memory_store_reminder.py ]; then
        echo "Backing up existing memory_store_reminder.py..."
        mv ~/.claude/hooks/memory_store_reminder.py ~/.claude/hooks/memory_store_reminder.py.backup.$(date +%s)
    fi
    cp hooks/memory_store_reminder.py ~/.claude/hooks/
    chmod +x ~/.claude/hooks/memory_store_reminder.py
    echo "Installed memory_store_reminder.py"
fi

if [ -f ~/.claude/hooks/todowrite_memory_recall.py ] && [ -f ~/.claude/hooks/memory_store_reminder.py ]; then
    echo -e "${GREEN}✓ Hooks installed${NC}\n"
else
    echo -e "${YELLOW}⚠ Hooks not found in project. They may need to be created manually.${NC}\n"
fi

# Step 7: Update ~/.claude.json
echo -e "${YELLOW}[7/10] Updating Claude configuration...${NC}"

CLAUDE_CONFIG=~/.claude.json
PROJECT_DIR=$(pwd)
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"

# Check if venv exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo -e "${YELLOW}Warning: Virtual environment not found. Using system Python.${NC}"
    VENV_PYTHON=$(which python3)
fi

# Backup existing config
if [ -f "$CLAUDE_CONFIG" ]; then
    cp "$CLAUDE_CONFIG" "$CLAUDE_CONFIG.backup.$(date +%s)"
    echo "Backed up existing config to $CLAUDE_CONFIG.backup.*"
fi

# Create or update MCP config using Python
python3 << 'EOF'
import json
import os
import sys

config_path = os.path.expanduser("~/.claude.json")
project_dir = os.environ.get("PROJECT_DIR", os.getcwd())
venv_python = os.environ.get("VENV_PYTHON", sys.executable)

# Load existing config or create new
if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
else:
    config = {}

# Ensure mcpServers exists
if 'mcpServers' not in config:
    config['mcpServers'] = {}

# Get API key from .env if exists
openai_key = "YOUR_OPENAI_API_KEY_HERE"
env_path = os.path.join(project_dir, ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            if line.startswith("OPENAI_API_KEY="):
                key = line.split("=", 1)[1].strip()
                if key and key != "your-openai-api-key-here":
                    openai_key = key
                    break

# Add memory server config
config['mcpServers']['memory'] = {
    "type": "stdio",
    "command": venv_python,
    "args": [f"{project_dir}/src/qdrant_memory_mcp/__main__.py"],
    "env": {
        "QDRANT_URL": "http://localhost:6333",
        "OPENAI_API_KEY": openai_key
    }
}

# Write back
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print("✓ MCP server configured in ~/.claude.json")
if openai_key == "YOUR_OPENAI_API_KEY_HERE":
    print("⚠ Warning: You still need to add your OpenAI API key")
EOF

echo -e "${GREEN}✓ Configuration updated${NC}\n"

# Step 8: Setup environment variables
echo -e "${YELLOW}[8/10] Setting up environment variables...${NC}"

if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "Created .env from .env.example"
    else
        cat > .env << 'ENVEOF'
# Qdrant Configuration
QDRANT_URL=http://localhost:6333

# OpenAI Configuration (for embeddings)
OPENAI_API_KEY=your-openai-api-key-here

# Optional: Voyage AI (alternative embedding provider)
# VOYAGE_API_KEY=your-voyage-api-key-here

# Optional: Nomic AI (alternative embedding provider)
# NOMIC_API_KEY=your-nomic-api-key-here
ENVEOF
        echo "Created default .env file"
    fi
    echo -e "${YELLOW}Please edit .env with your API keys (required):${NC}"
    echo "  nano .env"
else
    echo ".env file already exists"
fi
echo ""

# Step 9: Verify installation
echo -e "${YELLOW}[9/10] Verifying installation...${NC}"

# Check Qdrant
if curl -s http://localhost:6333/healthz > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Qdrant: Running on port 6333${NC}"
else
    echo -e "${RED}✗ Qdrant: Not responding${NC}"
fi

# Check Python package
if python3 -c "import qdrant_memory_mcp" 2>/dev/null; then
    echo -e "${GREEN}✓ Python package: Installed${NC}"
else
    echo -e "${RED}✗ Python package: Not found${NC}"
fi

# Check skills
SKILLS_OK=true
if [ -d ~/.claude/skills/coder-memory-recall ]; then
    echo -e "${GREEN}✓ Skill: coder-memory-recall${NC}"
else
    echo -e "${YELLOW}⚠ Skill: coder-memory-recall not found${NC}"
    SKILLS_OK=false
fi

if [ -d ~/.claude/skills/coder-memory-store ]; then
    echo -e "${GREEN}✓ Skill: coder-memory-store${NC}"
else
    echo -e "${YELLOW}⚠ Skill: coder-memory-store not found${NC}"
    SKILLS_OK=false
fi

# Check subagent
if [ -d ~/.claude/subagents/memory-only ]; then
    echo -e "${GREEN}✓ Subagent: memory-only${NC}"
else
    echo -e "${YELLOW}⚠ Subagent: memory-only not found${NC}"
fi

# Check hooks
if [ -f ~/.claude/hooks/todowrite_memory_recall.py ]; then
    echo -e "${GREEN}✓ Hook: todowrite_memory_recall.py${NC}"
else
    echo -e "${YELLOW}⚠ Hook: todowrite_memory_recall.py not found${NC}"
fi

if [ -f ~/.claude/hooks/memory_store_reminder.py ]; then
    echo -e "${GREEN}✓ Hook: memory_store_reminder.py${NC}"
else
    echo -e "${YELLOW}⚠ Hook: memory_store_reminder.py not found${NC}"
fi

# Check config
if grep -q '"memory"' ~/.claude.json 2>/dev/null; then
    echo -e "${GREEN}✓ Configuration: MCP server configured${NC}"
else
    echo -e "${RED}✗ Configuration: MCP server not found in ~/.claude.json${NC}"
fi

# Step 10: Print next steps
echo ""
echo -e "${GREEN}=== Installation Complete! ===${NC}\n"

echo -e "${YELLOW}Next steps:${NC}"

# Check if API key is set
if grep -q "your-openai-api-key-here" .env 2>/dev/null || grep -q "YOUR_OPENAI_API_KEY_HERE" ~/.claude.json 2>/dev/null; then
    echo -e "${RED}1. REQUIRED: Add your OpenAI API key${NC}"
    echo "   Edit .env file:"
    echo "   nano .env"
    echo ""
    echo "   Then update ~/.claude.json manually or re-run this installer"
    echo ""
fi

echo "2. Restart Claude Code completely (quit and reopen)"
echo ""
echo "3. Test the memory system:"
echo "   - Complex task will auto-trigger memory recall"
echo "   - Try: 'Search memory for API rate limiting patterns'"
echo "   - Try: 'Store this learning: Always check rate limits for external APIs'"
echo ""

echo -e "${YELLOW}Troubleshooting:${NC}"
echo "- Check Qdrant: docker logs qdrant-memory"
echo "- Check MCP server: Look for 'memory' in Claude Code MCP status"
echo "- Verify skills: ls -la ~/.claude/skills/"
echo "- Verify config: cat ~/.claude.json | grep -A 10 memory"
echo ""

echo -e "${YELLOW}Management:${NC}"
echo "- Stop Qdrant: docker-compose down"
echo "- Start Qdrant: docker-compose up -d"
echo "- Uninstall: ./uninstall.sh"
echo ""

echo -e "${GREEN}Documentation:${NC}"
echo "- README.md - Project overview"
echo "- QUICKSTART.md - Usage guide"
echo "- docs/INSTALLATION_PACKAGING.md - Installation details"
echo "- docs/BACKLOG.md - Development roadmap"
echo ""

if [ "$SKILLS_OK" = true ]; then
    echo -e "${GREEN}Memory system ready to use!${NC}"
    echo "The memory system will auto-trigger on complex tasks."
else
    echo -e "${YELLOW}Installation completed with warnings. Check skill installation above.${NC}"
fi
