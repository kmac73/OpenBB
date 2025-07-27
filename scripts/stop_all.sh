#!/bin/bash

# OpenBB All Services Stop Script
# Stops API server, Jupyter Lab, and cleans up processes

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== Stopping OpenBB Services ===${NC}"
echo ""

# Stop Jupyter Lab (using your existing alias logic)
echo -e "${BLUE}Stopping Jupyter Lab...${NC}"
if pgrep -f jupyter-lab > /dev/null; then
    pkill -f jupyter-lab
    echo -e "${GREEN}✅ Jupyter Lab stopped${NC}"
else
    echo -e "${YELLOW}ℹ️  No Jupyter Lab processes found${NC}"
fi

# Stop API Server
echo -e "${BLUE}Stopping API Server...${NC}"
if [ -f ~/.openbb_api.pid ]; then
    API_PID=$(cat ~/.openbb_api.pid)
    if kill -0 $API_PID 2>/dev/null; then
        kill $API_PID
        echo -e "${GREEN}✅ API Server stopped (PID: $API_PID)${NC}"
    else
        echo -e "${YELLOW}ℹ️  API Server process not found${NC}"
    fi
    rm -f ~/.openbb_api.pid
else
    # Fallback: kill by process name
    if pgrep -f "uvicorn.*openbb_core.api.rest_api" > /dev/null; then
        pkill -f "uvicorn.*openbb_core.api.rest_api"
        echo -e "${GREEN}✅ API Server stopped${NC}"
    else
        echo -e "${YELLOW}ℹ️  No API Server processes found${NC}"
    fi
fi

# Clean up any remaining OpenBB processes
echo -e "${BLUE}Cleaning up remaining processes...${NC}"
if pgrep -f openbb > /dev/null; then
    pkill -f openbb || true
    echo -e "${GREEN}✅ Cleaned up OpenBB processes${NC}"
fi

echo ""
echo -e "${GREEN}=== All OpenBB services stopped ===${NC}"
echo ""
echo -e "${YELLOW}Log files preserved:${NC}"
echo -e "  ~/jupyter.log"
echo -e "  ~/openbb_api.log"
echo ""