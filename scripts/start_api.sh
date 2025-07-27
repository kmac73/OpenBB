#!/bin/bash

# OpenBB Platform API Startup Script
# Starts the FastAPI REST API server

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== Starting OpenBB Platform API Server ===${NC}"

# Ensure we're in the correct base directory
BASE_DIR="/home/kmm/kevin/git/OpenBB"
cd "$BASE_DIR"

# Activate OpenBB-env
echo -e "${BLUE}Activating OpenBB-env environment...${NC}"
source ~/miniconda3/etc/profile.d/conda.sh
conda activate OpenBB-env

# Check if openbb is installed
if ! python -c "import openbb" 2>/dev/null; then
    echo -e "${YELLOW}⚠ OpenBB Platform not found. Please run ./install_openbb.sh first${NC}"
    exit 1
fi

# Default configuration
HOST="${OPENBB_API_HOST:-0.0.0.0}"
PORT="${OPENBB_API_PORT:-8000}"
RELOAD="${OPENBB_API_RELOAD:-true}"

echo -e "${GREEN}✓${NC} Starting API server..."
echo -e "  Host: ${YELLOW}$HOST${NC}"
echo -e "  Port: ${YELLOW}$PORT${NC}"
echo -e "  Reload: ${YELLOW}$RELOAD${NC}"
echo ""
echo -e "${GREEN}✓${NC} API Documentation will be available at: ${YELLOW}http://$HOST:$PORT/docs${NC}"
echo -e "${GREEN}✓${NC} API will be available at: ${YELLOW}http://$HOST:$PORT${NC}"
echo ""

# Set reload flag
if [ "$RELOAD" = "true" ]; then
    RELOAD_FLAG="--reload"
else
    RELOAD_FLAG=""
fi

# Start the server
echo -e "${BLUE}Starting uvicorn server...${NC}"
echo ""

# Use exec to replace the shell process with uvicorn
exec uvicorn openbb_core.api.rest_api:app \
    --host "$HOST" \
    --port "$PORT" \
    $RELOAD_FLAG \
    2>&1