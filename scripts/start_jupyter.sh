#!/bin/bash

# OpenBB Jupyter Lab Startup Script
# Integrates with existing jlab aliases and starts Jupyter Lab with OpenBB environment

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== Starting Jupyter Lab for OpenBB ===${NC}"

# Ensure we're in the correct base directory
BASE_DIR="/home/kmm/kevin/git/OpenBB"
cd "$BASE_DIR"

# Check and activate OpenBB-env if not already active
if [ "$CONDA_DEFAULT_ENV" != "OpenBB-env" ]; then
    echo -e "${BLUE}Activating OpenBB-env environment...${NC}"
    source ~/miniconda3/etc/profile.d/conda.sh
    conda activate OpenBB-env
    echo -e "${GREEN}✓${NC} Activated OpenBB-env environment"
else
    echo -e "${GREEN}✓${NC} Using conda environment: ${YELLOW}$CONDA_DEFAULT_ENV${NC}"
fi

# Check if jupyter is already running
if pgrep -f jupyter-lab > /dev/null; then
    echo -e "${YELLOW}⚠ Jupyter Lab is already running${NC}"
    echo -e "  Use ${YELLOW}jps${NC} to see processes"
    echo -e "  Use ${YELLOW}jstop${NC} to stop existing processes"
    echo -e "${GREEN}✅ Jupyter Lab is accessible at: ${YELLOW}http://localhost:8888${NC}"
    exit 0
fi

# Check if jupyter is installed
if ! command -v jupyter &> /dev/null; then
    echo -e "${YELLOW}⚠ Jupyter not found. Installing...${NC}"
    pip install jupyterlab notebook
fi

echo -e "${GREEN}✓${NC} Starting Jupyter Lab in background..."
echo -e "  IP: ${YELLOW}0.0.0.0${NC}"
echo -e "  Port: ${YELLOW}8888${NC}"
echo -e "  Log file: ${YELLOW}../logs/jupyter.log${NC}"
echo ""
echo -e "${GREEN}✓${NC} Jupyter Lab will be available at: ${YELLOW}http://localhost:8888${NC}"
echo -e "${GREEN}✓${NC} Notebooks available in: ${YELLOW}./notebooks/${NC}"
echo -e "${GREEN}✓${NC} Market data accessible at: ${YELLOW}../market_data/${NC}"
echo ""

# Change to notebooks directory, create if it doesn't exist
if [ ! -d "notebooks" ]; then
    echo -e "${YELLOW}⚠ Creating notebooks directory...${NC}"
    mkdir -p notebooks
fi

cd notebooks
echo -e "${BLUE}Starting in notebooks/ directory...${NC}"

# Ensure market_data is accessible (create symlink if needed and doesn't exist)
if [ ! -e "market_data" ] && [ -d "../market_data" ]; then
    echo -e "${BLUE}Creating symlink to market_data...${NC}"
    ln -s ../market_data market_data
    echo -e "${GREEN}✓${NC} market_data/ accessible from notebooks"
fi

# Start Jupyter Lab in background with logging (matches your alias style)
echo -e "${BLUE}Starting Jupyter Lab...${NC}"
nohup jupyter lab \
    --ip=0.0.0.0 \
    --port=8888 \
    --no-browser \
    --allow-root > ../logs/jupyter.log 2>&1 &

# Wait a moment for startup
sleep 2

# Check if it started successfully
if pgrep -f jupyter-lab > /dev/null; then
    echo -e "${GREEN}✅ Jupyter Lab started successfully${NC}"
    echo ""
    echo -e "${YELLOW}Useful commands:${NC}"
    echo -e "  ${YELLOW}jps${NC}     - Show Jupyter processes"
    echo -e "  ${YELLOW}jstop${NC}   - Stop Jupyter Lab"
    echo -e "  ${YELLOW}jkill${NC}   - Kill all Jupyter processes"
    echo -e "  ${YELLOW}tail -f ../logs/jupyter.log${NC} - View logs"
else
    echo -e "${RED}❌ Failed to start Jupyter Lab${NC}"
    echo -e "Check logs: ${YELLOW}cat ../logs/jupyter.log${NC}"
    exit 1
fi