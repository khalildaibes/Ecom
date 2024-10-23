param (
    [string]$DropletName,
    [string]$Region,
    [string]$Size,
    [string]$Image,
    [string]$PublicKeyPath
)

# Exit the script on any error
$ErrorActionPreference = "Stop"

# Validate if public key exists
if (-not (Test-Path -Path $PublicKeyPath)) {
    Write-Host "Public key file not found at: $PublicKeyPath"
    exit 1
}

# Read the SSH public key from the provided file path
$PublicKey = Get-Content -Path $PublicKeyPath

# Map regions to DigitalOcean's internal region codes
switch ($Region) {
    "New York" { $RegionCode = "nyc1" }
    "San Francisco" { $RegionCode = "sfo1" }
    "Amsterdam" { $RegionCode = "ams3" }
    "Singapore" { $RegionCode = "sgp1" }
    "London" { $RegionCode = "lon1" }
    "Frankfurt" { $RegionCode = "fra1" }
    "Toronto" { $RegionCode = "tor1" }
    "Bangalore" { $RegionCode = "blr1" }
    "Sydney" { $RegionCode = "syd1" }
    Default {
        Write-Host "Invalid region"
        exit 1
    }
}

# Create the cloud-config user-data string dynamically with the public key
$userData = @"
#cloud-config
users:
  - name: root
    ssh-authorized-keys:
      - $PublicKey
    sudo: ["ALL=(ALL) NOPASSWD:ALL"]
    groups: sudo
    shell: /bin/bash
runcmd:
  - sed -i "s/PasswordAuthentication no/PasswordAuthentication yes/" /etc/ssh/sshd_config
  - ufw allow 22/tcp
  - systemctl restart sshd
"@

# Create the droplet and capture the output
Write-Host "Creating Droplet: $DropletName in region $RegionCode with size $Size and image $Image"

# Command to create the droplet using the doctl CLI
$DropletId = C:\WINDOWS\system32\config\systemprofile\doctl\doctl.exe compute droplet create $DropletName --size $Size --image $Image --region $RegionCode --user-data $userData --format ID --no-header --wait

if (-not $DropletId) {
    Write-Host "Failed to create droplet."
    exit 1
}

# Store the Droplet ID in a temporary file for later use
$TempFile = "$env:TEMP\droplet_id.txt"
Set-Content -Path $TempFile -Value $DropletId

Write-Host "Droplet $DropletName created with ID: $DropletId"
