#!/bin/bash

# JJ Pastebin Vim Plugin Installation Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}JJ Pastebin Vim Plugin Installer${NC}"
echo "=================================="

# Check if vim is installed
if ! command -v vim &> /dev/null; then
    echo -e "${RED}Error: Vim is not installed or not in PATH${NC}"
    exit 1
fi

# Check if curl is installed
if ! command -v curl &> /dev/null; then
    echo -e "${RED}Error: curl is required but not installed${NC}"
    exit 1
fi

# Create vim directories
echo -e "${BLUE}Creating Vim directories...${NC}"
mkdir -p ~/.vim/plugin
mkdir -p ~/.vim/doc

# Copy plugin files
echo -e "${BLUE}Installing plugin files...${NC}"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Copy the main plugin file
if [ -f "$SCRIPT_DIR/jj-pastebin.vim" ]; then
    cp "$SCRIPT_DIR/jj-pastebin.vim" ~/.vim/plugin/
    echo -e "${GREEN}✓ Installed jj-pastebin.vim${NC}"
else
    echo -e "${RED}✗ jj-pastebin.vim not found in $SCRIPT_DIR${NC}"
    exit 1
fi

# Copy the documentation file
if [ -f "$SCRIPT_DIR/jj-pastebin.txt" ]; then
    cp "$SCRIPT_DIR/jj-pastebin.txt" ~/.vim/doc/
    echo -e "${GREEN}✓ Installed jj-pastebin.txt${NC}"
else
    echo -e "${YELLOW}⚠ Documentation file not found, skipping...${NC}"
fi

# Generate helptags
echo -e "${BLUE}Generating help tags...${NC}"
vim -c "helptags ~/.vim/doc" -c "quit" 2>/dev/null || true

echo ""
echo -e "${GREEN}Installation completed successfully!${NC}"
echo ""
echo -e "${BLUE}Configuration:${NC}"
echo "Add these lines to your ~/.vimrc file:"
echo ""
echo "\" JJ Pastebin configuration"
echo "let g:jj_pastebin_url = 'http://localhost:8000'"
echo "let g:jj_pastebin_username = 'your_username'  \" Optional"
echo "let g:jj_pastebin_password = 'your_password'  \" Optional"
echo ""
echo -e "${BLUE}Usage:${NC}"
echo ":JJ                    - Paste entire buffer"
echo ":JJ My Title           - Paste with custom title"
echo ":5,10JJ                - Paste lines 5-10"
echo ":'<,'>JJ               - Paste visual selection"
echo ":JJPriv                - Create private paste"
echo ":JJPub                 - Create public paste"
echo ":JJConfig              - Show configuration"
echo ""
echo -e "${BLUE}Help:${NC}"
echo ":help jj-pastebin      - View detailed documentation"
echo ""
echo -e "${GREEN}Happy pasting! 🎉${NC}" 