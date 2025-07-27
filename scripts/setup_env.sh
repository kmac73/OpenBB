#!/bin/bash

# Ensure we're in the correct base directory
BASE_DIR="/home/kmm/kevin/git/OpenBB"
cd "$BASE_DIR"

# Set fixed environment name
REPO_NAME="OpenBB"
ENV_NAME="OpenBB-env"

echo "Setting up conda environment: $ENV_NAME"
echo "Repository: $REPO_NAME"

# Check if environment.yml exists in current directory
if [ ! -f "environment.yml" ]; then
    echo "Error: environment.yml not found in current directory"
    echo "Please copy the environment.yml file to this repository's root directory"
    exit 1
fi

# Create conda environment from environment.yml
echo "Creating conda environment from environment.yml..."
conda env create -f environment.yml -n "$ENV_NAME"

if [ $? -ne 0 ]; then
    echo "Error: Failed to create conda environment"
    exit 1
fi

# Activate the environment
echo "Activating environment: $ENV_NAME"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"

# Install the environment as a Jupyter kernel
echo "Installing Jupyter kernel..."
python -m ipykernel install --user --name "$ENV_NAME" --display-name "Python ($REPO_NAME)"

if [ $? -eq 0 ]; then
    echo "✅ Successfully created environment: $ENV_NAME"
    echo "✅ Jupyter kernel installed: Python ($REPO_NAME)"
    echo ""
    echo "To activate this environment, run:"
    echo "  conda activate $ENV_NAME"
    echo ""
    echo "To see this kernel in Jupyter, restart your Jupyter server if it's already running"
    echo ""
    echo "Environment location: $(conda info --envs | grep $ENV_NAME | awk '{print $2}')"
else
    echo "❌ Environment created but kernel installation failed"
    exit 1
fi