#!/bin/bash

# OpenBB All Services Startup Script
# Starts API server, Jupyter Lab, and optionally CLI

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== OpenBB Complete Environment Startup ===${NC}"
echo ""

# Check and activate OpenBB-env if not already active
echo -e "${BLUE}Checking conda environment...${NC}"
if [ "$CONDA_DEFAULT_ENV" != "OpenBB-env" ]; then
    echo -e "${YELLOW}⚠ OpenBB-env not active. Activating...${NC}"
    source ~/miniconda3/etc/profile.d/conda.sh
    conda activate OpenBB-env
    echo -e "${GREEN}✓${NC} Activated OpenBB-env environment"
else
    echo -e "${GREEN}✓${NC} OpenBB-env already active"
fi
echo ""

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -i :$port > /dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

if ! python -c "import openbb" 2>/dev/null; then
    echo -e "${RED}❌ OpenBB Platform not found${NC}"
    echo -e "${YELLOW}Please run ./install_openbb.sh first${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} OpenBB Platform installed"

# Start Jupyter Lab
echo ""
echo -e "${BLUE}Starting Jupyter Lab...${NC}"
./start_jupyter.sh

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Jupyter Lab started${NC}"
else
    echo -e "${RED}❌ Failed to start Jupyter Lab${NC}"
fi

# Wait a moment
sleep 1

# Start API Server
echo ""
echo -e "${BLUE}Starting API Server...${NC}"

if check_port 8000; then
    echo -e "${YELLOW}⚠ Port 8000 is already in use${NC}"
    echo -e "  API server may already be running"
else
    # Start API server in background
    nohup ./start_api.sh > ~/openbb_api.log 2>&1 &
    API_PID=$!
    
    # Wait for API to start with retry logic
    echo -e "${BLUE}Waiting for API server to start...${NC}"
    for i in {1..10}; do
        sleep 2
        if check_port 8000; then
            echo -e "${GREEN}✅ API Server started (PID: $API_PID)${NC}"
            echo $API_PID > ~/.openbb_api.pid
            break
        fi
        if [ $i -eq 10 ]; then
            echo -e "${RED}❌ Failed to start API Server after 20 seconds${NC}"
            echo -e "Check logs: ${YELLOW}cat ~/openbb_api.log${NC}"
        else
            echo -e "${YELLOW}⏳ Attempt $i/10 - waiting...${NC}"
        fi
    done
fi

# Summary
echo ""
echo -e "${GREEN}=== Services Status ===${NC}"
echo ""

# Jupyter status
if pgrep -f jupyter-lab > /dev/null; then
    echo -e "${GREEN}✅ Jupyter Lab${NC}      - http://localhost:8888"
    echo -e "   Logs: ${YELLOW}tail -f ~/jupyter.log${NC}"
    echo -e "   Stop: ${YELLOW}jstop${NC}"
else
    echo -e "${RED}❌ Jupyter Lab${NC}      - Not running"
fi

# API status
if check_port 8000; then
    echo -e "${GREEN}✅ REST API${NC}         - http://localhost:8000"
    echo -e "   Docs: ${YELLOW}http://localhost:8000/docs${NC}"
    echo -e "   Logs: ${YELLOW}tail -f ~/openbb_api.log${NC}"
else
    echo -e "${RED}❌ REST API${NC}         - Not running"
fi

echo ""
echo -e "${BLUE}Additional Commands:${NC}"
echo -e "  ${YELLOW}./start_cli.sh${NC}  - Start OpenBB CLI"
echo -e "  ${YELLOW}./stop_all.sh${NC}   - Stop all services"
echo ""
echo -e "${GREEN}Happy investing with OpenBB! 🚀${NC}"