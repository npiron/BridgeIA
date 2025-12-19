#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== BridgeIA Local Setup & Run ===${NC}"

# Check for Python 3.11+
if ! command -v python3 &> /dev/null; then
    echo "Python 3 could not be found."
    exit 1
fi

# Check for Poetry
if ! command -v poetry &> /dev/null; then
    echo "Poetry could not be found."
    exit 1
fi

echo -e "${GREEN}Installing dependencies...${NC}"
poetry install

echo -e "${GREEN}Starting the game...${NC}"
poetry run python -m bridgeia.main
