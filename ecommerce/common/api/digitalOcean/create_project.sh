#!/bin/bash
set -e

PROJECT_NAME=$1

# Create the project
echo "Creating DigitalOcean project: $PROJECT_NAME"
doctl projects create --name "$PROJECT_NAME" --purpose "Frontend development"
