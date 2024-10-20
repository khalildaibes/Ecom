#!/bin/bash
set -e

DROPLET_NAME=$1
REGION=$2
SIZE=$3
IMAGE=$4

# Map regions to DigitalOcean's internal region codes
case $REGION in
    "New York") REGION_CODE="nyc1";;
    "San Francisco") REGION_CODE="sfo1";;
    "Amsterdam") REGION_CODE="ams3";;
    "Singapore") REGION_CODE="sgp1";;
    "London") REGION_CODE="lon1";;
    "Frankfurt") REGION_CODE="fra1";;
    "Toronto") REGION_CODE="tor1";;
    "Bangalore") REGION_CODE="blr1";;
    "Sydney") REGION_CODE="syd1";;
    *) echo "Invalid region"; exit 1;;
esac

# Create the droplet and capture the output
echo "Creating Droplet: $DROPLET_NAME in region $REGION_CODE with size $SIZE and image $IMAGE"
DROPLET_ID=$(doctl compute droplet create $DROPLET_NAME --size $SIZE --image $IMAGE --region $REGION_CODE --format ID --no-header --wait)

if [ -z "$DROPLET_ID" ]; then
  echo "Failed to create droplet."
  exit 1
fi

# Store the Droplet ID in a temporary file for later use
echo $DROPLET_ID > /tmp/droplet_id.txt

echo "Droplet $DROPLET_NAME created with ID: $DROPLET_ID"
