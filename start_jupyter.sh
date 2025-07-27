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

# Activate alfa-class-env
echo -e "${BLUE}Activating alfa-class-env environment...${NC}"
source ~/miniconda3/etc/profile.d/conda.sh
conda activate alfa-class-env

# Check if in conda environment
if [ -n "$CONDA_DEFAULT_ENV" ]; then
    echo -e "${GREEN}✓${NC} Using conda environment: ${YELLOW}$CONDA_DEFAULT_ENV${NC}"
fi

# Check if jupyter is already running
if pgrep -f jupyter-lab > /dev/null; then
    echo -e "${GREEN}✅ Jupyter Lab is already running${NC}"
    echo -e "  Available at: ${YELLOW}http://localhost:8888${NC}"
    echo -e "  Use ${YELLOW}jps${NC} to see processes"
    echo -e "  Use ${YELLOW}jstop${NC} to stop existing processes"
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
echo -e "  Log file: ${YELLOW}~/jupyter.log${NC}"
echo ""
echo -e "${GREEN}✓${NC} Jupyter Lab will be available at: ${YELLOW}http://localhost:8888${NC}"
echo -e "${GREEN}✓${NC} Examples available in: ${YELLOW}./notebooks/examples/${NC}"
echo ""

# Change to notebooks directory if it exists
if [ -d "notebooks" ]; then
    cd notebooks
    echo -e "${BLUE}Starting in notebooks directory...${NC}"
fi

# Start Jupyter Lab in background with logging (matches your alias style)
echo -e "${BLUE}Starting Jupyter Lab...${NC}"
nohup jupyter lab \
    --ip=0.0.0.0 \
    --port=8888 \
    --no-browser \
    --allow-root > ~/jupyter.log 2>&1 &

# Wait a moment for startup
sleep 3

# Check if it started successfully
if pgrep -f jupyter-lab > /dev/null; then
    echo -e "${GREEN}✅ Jupyter Lab started successfully${NC}"
    echo ""
    echo -e "${YELLOW}Useful commands:${NC}"
    echo -e "  ${YELLOW}jps${NC}     - Show Jupyter processes"
    echo -e "  ${YELLOW}jstop${NC}   - Stop Jupyter Lab"
    echo -e "  ${YELLOW}jkill${NC}   - Kill all Jupyter processes"
    echo -e "  ${YELLOW}tail -f ~/jupyter.log${NC} - View logs"
else
    echo -e "${RED}❌ Failed to start Jupyter Lab${NC}"
    echo -e "Check logs: ${YELLOW}cat ~/jupyter.log${NC}"
    exit 1
fi