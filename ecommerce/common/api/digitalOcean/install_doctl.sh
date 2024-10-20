#!/bin/bash
set -e

# Check if doctl is already installed
if ! command -v doctl &> /dev/null; then
    echo "Installing doctl..."
    sudo snap install doctl
else
    echo "doctl is already installed"
fi
