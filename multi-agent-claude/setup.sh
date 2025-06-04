#!/bin/bash

echo "==================================="
echo "Multi-Agent Claude Setup Script"
echo "==================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

echo "Phase 1: Checking prerequisites..."
echo ""

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    print_status 0 "Node.js installed: $NODE_VERSION"
else
    print_status 1 "Node.js not installed"
    echo "  Please install Node.js from https://nodejs.org/"
fi

# Check npm
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    print_status 0 "npm installed: $NPM_VERSION"
else
    print_status 1 "npm not installed"
fi

# Check Rust
if command_exists rustc; then
    RUST_VERSION=$(rustc --version)
    print_status 0 "Rust installed: $RUST_VERSION"
else
    print_status 1 "Rust not installed"
    echo -e "  Run: ${YELLOW}./multi-agent-setup/install-rust.sh${NC}"
fi

# Check Cargo
if command_exists cargo; then
    CARGO_VERSION=$(cargo --version)
    print_status 0 "Cargo installed: $CARGO_VERSION"
else
    print_status 1 "Cargo not installed"
fi

echo ""
echo "Phase 2: Installing MCP servers..."
echo ""

# Function to install npm package globally
install_npm_package() {
    PACKAGE=$1
    echo -n "Installing $PACKAGE... "
    
    if npm list -g $PACKAGE >/dev/null 2>&1; then
        print_status 0 "already installed"
    else
        if npm install -g $PACKAGE >/dev/null 2>&1; then
            print_status 0 "installed successfully"
        else
            print_status 1 "installation failed"
        fi
    fi
}

# Install MCP servers
echo "Note: MCP servers from @anthropic namespace may not be publicly available yet."
echo "Checking for available MCP servers..."
echo ""

# These are placeholder package names - actual names may differ
install_npm_package "@modelcontextprotocol/server-filesystem"
install_npm_package "@modelcontextprotocol/server-github"

echo ""
echo "Phase 3: Setting up project structure..."
echo ""

# Create necessary directories
DIRS=("logs" "shared" "context/documentation" "context/project_specs")
for dir in "${DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        print_status 0 "Created directory: $dir"
    else
        print_status 0 "Directory exists: $dir"
    fi
done

# Make scripts executable
chmod +x scripts/*.py
print_status 0 "Made scripts executable"

echo ""
echo "Phase 4: Configuration..."
echo ""

# Check for Claude Desktop config
CLAUDE_CONFIG_DIR="$HOME/.config/claude-desktop"
if [ -d "$CLAUDE_CONFIG_DIR" ]; then
    print_status 0 "Claude Desktop config directory found"
    echo -e "  Update: ${YELLOW}$CLAUDE_CONFIG_DIR/claude_desktop_config.json${NC}"
    echo "  with MCP server configurations from config/mcp_config.json"
else
    print_status 1 "Claude Desktop config directory not found"
    echo "  Please install Claude Desktop first"
fi

echo ""
echo "Phase 5: Next steps..."
echo ""
echo "1. Install Rust if not already installed:"
echo "   ${YELLOW}./multi-agent-setup/install-rust.sh${NC}"
echo ""
echo "2. Configure MCP servers in Claude Desktop:"
echo "   Edit ${YELLOW}~/.config/claude-desktop/claude_desktop_config.json${NC}"
echo ""
echo "3. Update configuration files:"
echo "   - ${YELLOW}config/agents.json${NC} - Set number of agents and types"
echo "   - ${YELLOW}config/mcp_config.json${NC} - Update paths and tokens"
echo ""
echo "4. Test the setup:"
echo "   ${YELLOW}python3 scripts/start_session.py${NC}"
echo ""
echo "5. For Rust projects, run the cargo daemon:"
echo "   ${YELLOW}python3 scripts/cargo_daemon.py /path/to/rust/project${NC}"
echo ""

# Create a simple test script
cat > test_setup.py << 'EOF'
#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.task_manager import TaskManager

print("Testing Task Manager...")
manager = TaskManager()

# Test task claiming
if manager.claim_task("test_agent", "test_task"):
    print("✓ Task claiming works")
    manager.release_task("test_agent", "test_task")
else:
    print("✗ Task claiming failed")

# Test file locking
if manager.lock_file("test_agent", "test_file.py"):
    print("✓ File locking works")
    manager.release_file_lock("test_agent", "test_file.py")
else:
    print("✗ File locking failed")

print("\nBasic setup test complete!")
EOF

chmod +x test_setup.py
print_status 0 "Created test_setup.py"

echo ""
echo "Run ${YELLOW}./test_setup.py${NC} to test basic functionality"
echo ""
echo "Setup script complete!"