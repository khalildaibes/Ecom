#!/bin/bash
set -e

DROPLET_ID=$(cat /tmp/droplet_id.txt)

if [ -z "$DROPLET_ID" ]; then
  echo "Droplet ID not found. Cannot retrieve Droplet information."
  exit 1
fi

# Get droplet info in JSON format
DROPLET_INFO=$(doctl compute droplet get $DROPLET_ID --format ID,Name,PublicIPv4,Region,Memory,VCPUs,Disk,Image --no-header --output json)

echo "DROPLET_INFO: $DROPLET_INFO"
