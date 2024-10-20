#!/bin/bash
set -e

# Authenticate doctl using the provided token (DO_TOKEN is passed as an environment variable)
echo "Authenticating with DigitalOcean..."
doctl auth init -t $DO_TOKEN
