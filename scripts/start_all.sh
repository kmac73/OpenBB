#!/bin/bash

# OpenBB All Services Startup Script
# Starts API server, Jupyter Lab, and optionally CLI

set -e

# Parse command line arguments
STREAMLIT_ARG=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --streamlit=*)
            STREAMLIT_ARG="$1"
            shift
            ;;
        *)
            echo "Unknown option $1"
            echo "Usage: $0 [--streamlit=APP_FILE]"
            exit 1
            ;;
    esac
done

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== OpenBB Complete Environment Startup ===${NC}"
echo ""

# Ensure we're in the correct base directory
BASE_DIR="/home/kmm/kevin/git/OpenBB"
if [ "$(pwd)" != "$BASE_DIR/scripts" ]; then
    cd "$BASE_DIR/scripts"
fi

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
    # Try multiple methods to check if port is in use
    if lsof -i :$port > /dev/null 2>&1; then
        return 0  # Port is in use
    elif netstat -ln 2>/dev/null | grep -q ":$port "; then
        return 0  # Port is in use
    elif ss -ln 2>/dev/null | grep -q ":$port "; then
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

# Initialize OpenBB extensions (one-time build process)
echo ""
echo -e "${BLUE}Initializing OpenBB extensions...${NC}"
echo -e "${YELLOW}(This may take a few minutes on first run)${NC}"
python -c "from openbb import obb; print('OpenBB extensions initialized successfully')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} OpenBB extensions ready"
else
    echo -e "${YELLOW}⚠${NC} Extension initialization may be in progress"
fi

# Start Jupyter Lab
echo ""
echo -e "${BLUE}Starting Jupyter Lab...${NC}"
"$BASE_DIR/scripts/start_jupyter.sh"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Jupyter Lab started${NC}"
else
    echo -e "${RED}❌ Failed to start Jupyter Lab${NC}"
fi

# Wait a moment
sleep 1

# Start Streamlit App
echo ""
echo -e "${BLUE}Starting Streamlit App...${NC}"
if [ -n "$STREAMLIT_ARG" ]; then
    "$BASE_DIR/scripts/start_streamlit.sh" "$STREAMLIT_ARG"
else
    "$BASE_DIR/scripts/start_streamlit.sh"
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Streamlit App started${NC}"
else
    echo -e "${RED}❌ Failed to start Streamlit App${NC}"
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
    # Ensure logs directory exists
    mkdir -p "$BASE_DIR/logs"
    
    # Start API server in background using a more robust approach
    cd "$BASE_DIR"
    source ~/miniconda3/etc/profile.d/conda.sh
    conda activate OpenBB-env
    nohup uvicorn openbb_core.api.rest_api:app --host 0.0.0.0 --port 8000 > logs/openbb_api.log 2>&1 &
    API_PID=$!
    
    # Wait for API to start with retry logic
    echo -e "${BLUE}Waiting for API server to start...${NC}"
    API_STARTED=false
    for i in {1..15}; do
        sleep 3
        if check_port 8000; then
            echo -e "${GREEN}✅ API Server started (PID: $API_PID)${NC}"
            echo $API_PID > ~/.openbb_api.pid
            API_STARTED=true
            break
        fi
        # Check if process is still running
        if ! kill -0 $API_PID 2>/dev/null; then
            echo -e "${RED}❌ API Server process died${NC}"
            echo -e "Check logs: ${YELLOW}cat ../logs/openbb_api.log${NC}"
            break
        fi
        echo -e "${YELLOW}⏳ Attempt $i/15 - waiting...${NC}"
    done
    
    if [ "$API_STARTED" = "false" ]; then
        echo -e "${RED}❌ Failed to start API Server after 45 seconds${NC}"
        echo -e "Check logs: ${YELLOW}cat logs/openbb_api.log${NC}"
        echo -e "Last few lines of log:"
        tail -n 10 logs/openbb_api.log 2>/dev/null || echo "No log content available"
    fi
fi

# Summary
echo ""
echo -e "${GREEN}=== Services Status ===${NC}"
echo ""

# Jupyter status
if pgrep -f jupyter-lab > /dev/null; then
    echo -e "${GREEN}✅ Jupyter Lab${NC}      - http://localhost:8888"
    echo -e "   Logs: ${YELLOW}tail -f ../logs/jupyter.log${NC}"
    echo -e "   Stop: ${YELLOW}jstop${NC}"
else
    echo -e "${RED}❌ Jupyter Lab${NC}      - Not running"
fi

# Streamlit status
if pgrep -f "streamlit run.*8501" > /dev/null; then
    echo -e "${GREEN}✅ Streamlit App${NC}    - http://localhost:8501"
    echo -e "   Logs: ${YELLOW}tail -f ../logs/streamlit.log${NC}"
    echo -e "   Stop: ${YELLOW}$BASE_DIR/scripts/stop_streamlit.sh${NC}"
else
    echo -e "${RED}❌ Streamlit App${NC}    - Not running"
fi

# API status
if check_port 8000; then
    echo -e "${GREEN}✅ REST API${NC}         - http://localhost:8000"
    echo -e "   Docs: ${YELLOW}http://localhost:8000/docs${NC}"
    echo -e "   Logs: ${YELLOW}tail -f ../logs/openbb_api.log${NC}"
else
    echo -e "${RED}❌ REST API${NC}         - Not running"
fi

echo ""
echo -e "${BLUE}Additional Commands:${NC}"
echo -e "  ${YELLOW}$BASE_DIR/scripts/start_cli.sh${NC}  - Start OpenBB CLI"
echo -e "  ${YELLOW}$BASE_DIR/scripts/stop_all.sh${NC}   - Stop all services"
echo ""
echo -e "${GREEN}Happy investing with OpenBB! 🚀${NC}"