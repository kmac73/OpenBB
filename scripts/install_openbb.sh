#!/bin/bash

# OpenBB Platform Installation Script
# This script sets up OpenBB Platform for local development and usage

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ensure we're in the correct base directory
BASE_DIR="/home/kmm/kevin/git/OpenBB"
cd "$BASE_DIR"

# Set fixed environment and repo name
REPO_NAME="OpenBB"
ENV_NAME="OpenBB-env"

echo -e "${BLUE}=== OpenBB Platform Installation Script ===${NC}"
echo -e "${BLUE}Repository: $REPO_NAME${NC}"
echo -e "${BLUE}Environment: $ENV_NAME${NC}"
echo ""

# Function to print status messages
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if we're in the correct directory
if [ ! -f "openbb_platform/pyproject.toml" ]; then
    print_error "Error: Not in OpenBB repository root directory"
    print_warning "Please run this script from the OpenBB repository root directory"
    exit 1
fi

# Check for required tools
echo -e "${BLUE}Checking prerequisites...${NC}"

# Check Python version
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_status "Python version: $PYTHON_VERSION"

# Check if Python version is >= 3.9
if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 9) else 1)'; then
    print_error "Python 3.9 or higher is required"
    exit 1
fi

# Check for Poetry
if ! command -v poetry &> /dev/null; then
    print_warning "Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
    
    if ! command -v poetry &> /dev/null; then
        print_error "Failed to install Poetry"
        print_warning "Please install Poetry manually: https://python-poetry.org/docs/#installation"
        exit 1
    fi
fi

print_status "Poetry found: $(poetry --version)"

# Setup Conda environment (optional)
if command -v conda &> /dev/null && [ -f "environment.yml" ]; then
    echo ""
    read -p "Do you want to create/update a Conda environment? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Setting up Conda environment...${NC}"
        
        # Check if environment already exists
        if conda env list | grep -q "^${ENV_NAME}"; then
            print_warning "Environment $ENV_NAME already exists. Updating..."
            conda env update -f environment.yml -n "$ENV_NAME"
        else
            print_status "Creating new environment: $ENV_NAME"
            conda env create -f environment.yml -n "$ENV_NAME"
        fi
        
        # Activate environment
        source "$(conda info --base)/etc/profile.d/conda.sh"
        conda activate "$ENV_NAME"
        
        # Install as Jupyter kernel
        python -m ipykernel install --user --name "$ENV_NAME" --display-name "Python ($REPO_NAME)"
        print_status "Jupyter kernel installed"
    fi
fi

# Install OpenBB Platform
echo ""
echo -e "${BLUE}Installing OpenBB Platform...${NC}"

# Check for command line argument for installation method
if [ -n "$1" ]; then
    REPLY="$1"
    echo "Using command line argument: $REPLY"
else
    # Option 1: Development installation (from source)
    echo ""
    echo "Choose installation method:"
    echo "1) Development installation (editable, from source)"
    echo "2) Production installation (pip install openbb)"
    echo "3) Production with all extensions (pip install openbb[all])"
    read -p "Enter choice (1-3): " -n 1 -r
    echo
fi

case $REPLY in
    1)
        echo -e "${BLUE}Installing in development mode...${NC}"
        cd openbb_platform
        
        # Install platform dependencies
        print_status "Installing platform core and extensions..."
        python dev_install.py --extras
        
        # Install CLI separately if requested
        echo ""
        read -p "Do you want to install the CLI as well? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Installing CLI..."
            python dev_install.py --cli
        fi
        
        cd ..
        print_status "Development installation completed"
        ;;
    2)
        echo -e "${BLUE}Installing production version...${NC}"
        pip install openbb
        print_status "Production installation completed"
        ;;
    3)
        echo -e "${BLUE}Installing production version with all extensions...${NC}"
        pip install "openbb[all]"
        print_status "Production installation with all extensions completed"
        ;;
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

# Install CLI separately if not already done
if [ "$REPLY" != "1" ]; then
    echo ""
    read -p "Do you want to install the CLI? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip install openbb-cli
        print_status "CLI installed"
    fi
fi

# Create user settings directory
echo ""
echo -e "${BLUE}Setting up user configuration...${NC}"
mkdir -p ~/.openbb_platform

# Create sample user settings if it doesn't exist
if [ ! -f ~/.openbb_platform/user_settings.json ]; then
    cat > ~/.openbb_platform/user_settings.json << 'EOF'
{
  "credentials": {
    "fmp_api_key": "REPLACE_ME",
    "polygon_api_key": "REPLACE_ME",
    "benzinga_api_key": "REPLACE_ME", 
    "fred_api_key": "REPLACE_ME",
    "alpha_vantage_api_key": "REPLACE_ME",
    "intrinio_api_key": "REPLACE_ME"
  },
  "preferences": {
    "output_type": "OBBject"
  }
}
EOF
    print_status "Created sample user_settings.json"
    print_warning "Edit ~/.openbb_platform/user_settings.json to add your API keys"
fi

# Installation complete
echo ""
echo -e "${GREEN}=== Installation Complete! ===${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Add your API keys to ~/.openbb_platform/user_settings.json"
echo "2. Test the installation:"
echo "   ${YELLOW}python -c \"from openbb import obb; print(obb.equity.price.historical('AAPL'))\"${NC}"
echo ""

if command -v conda &> /dev/null && conda env list | grep -q "^${ENV_NAME}"; then
    echo "3. To activate your conda environment:"
    echo "   ${YELLOW}conda activate $ENV_NAME${NC}"
    echo ""
fi

echo "4. To start the REST API server:"
echo "   ${YELLOW}uvicorn openbb_core.api.rest_api:app --host 0.0.0.0 --port 8000 --reload${NC}"
echo ""

echo "5. To start the CLI:"
echo "   ${YELLOW}openbb${NC}"
echo ""

echo -e "${GREEN}Happy investing with OpenBB! 🚀${NC}"