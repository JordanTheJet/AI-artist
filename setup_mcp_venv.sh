#!/bin/bash
# Setup script for AI Artist MCP Server virtual environment

set -e  # Exit on error

echo "=========================================="
echo "AI Artist MCP Server Setup"
echo "=========================================="
echo

# Check if Python 3.11 is available
if ! command -v python3.11 &> /dev/null; then
    echo "❌ Python 3.11 is required but not found"
    echo "Please install Python 3.11 first"
    exit 1
fi

echo "✓ Python 3.11 found"

# Create virtual environment
echo
echo "Creating virtual environment with Python 3.11..."
python3.11 -m venv mcp-venv

echo "✓ Virtual environment created"

# Upgrade pip
echo
echo "Upgrading pip..."
mcp-venv/bin/pip install --upgrade pip -q

echo "✓ pip upgraded"

# Install dependencies
echo
echo "Installing dependencies (this may take a few minutes)..."
echo "Note: PyTorch is ~2GB and may take a while to download..."
mcp-venv/bin/pip install -r requirements.txt -q

echo "✓ Dependencies installed"

# Verify installation
echo
echo "Verifying installation..."
if mcp-venv/bin/python -c "from app.services.clip_service import CLIPService; from mcp.server import Server" 2>/dev/null; then
    echo "✓ All imports successful"
else
    echo "❌ Import verification failed"
    exit 1
fi

# Get absolute path
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_PYTHON="$SCRIPT_DIR/mcp-venv/bin/python"
MCP_SERVER="$SCRIPT_DIR/mcp_server.py"

echo
echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo
echo "Add this to your Claude Code config:"
echo
echo "{"
echo "  \"mcpServers\": {"
echo "    \"ai-artist\": {"
echo "      \"command\": \"$VENV_PYTHON\","
echo "      \"args\": ["
echo "        \"$MCP_SERVER\""
echo "      ],"
echo "      \"env\": {}"
echo "    }"
echo "  }"
echo "}"
echo
echo "Configuration file location:"
echo "  macOS: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo "  Windows: %APPDATA%\\Claude\\claude_desktop_config.json"
echo "  Linux: ~/.config/Claude/claude_desktop_config.json"
echo
echo "After adding the config, restart Claude Code to load the MCP server."
echo
