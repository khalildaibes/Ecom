#!/bin/bash
KHALIL_PASS=$1
GITHUB_TOKEN=$2
DROPLET_NAME=$3
VPC_IP=$4
NODE_VERSION="20.5.0"

# Check if all required arguments are passed
if [ -z "$KHALIL_PASS" ] || [ -z "$GITHUB_TOKEN" ] || [ -z "$DROPLET_NAME" ] || [ -z "$VPC_IP" ]; then
    echo "Usage: $0 <KHALIL_PASS> <GITHUB_TOKEN> <DROPLET_NAME> <VPC_IP>"
    exit 1
fi
echo "cloning the git repo"

C:\WINDOWS\system32\config\systemprofile\doctl\doctl.exe compute ssh $DropletID --ssh-command "git clone https://github.com/khalildaibes/strapi_setup.git" --ssh-key-path "C:\Users\Admin\.ssh\id_ed25519"

echo "executing the code"
C:\WINDOWS\system32\config\systemprofile\doctl\doctl.exe compute ssh $DropletID --ssh-command "cd strapi_setup && ./setup_strapi.sh " --ssh-key-path "C:\Users\Admin\.ssh\id_ed25519"
