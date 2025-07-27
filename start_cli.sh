#!/bin/bash

# OpenBB CLI Startup Script
# Starts the OpenBB Command Line Interface

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== Starting OpenBB CLI ===${NC}"

# Activate alfa-class-env
echo -e "${BLUE}Activating alfa-class-env environment...${NC}"
source ~/miniconda3/etc/profile.d/conda.sh
conda activate alfa-class-env

# Check if openbb-cli is installed
if ! command -v openbb &> /dev/null; then
    echo -e "${YELLOW}⚠ OpenBB CLI not found. Please run ./install_openbb.sh first${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Starting OpenBB CLI..."
echo ""

# Start the CLI
exec openbb