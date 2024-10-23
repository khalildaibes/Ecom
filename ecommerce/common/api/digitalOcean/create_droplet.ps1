# create_droplet.ps1
param (
    [string]$DropletName,
    [string]$Region,
    [string]$Size,
    [string]$Image
)

# Exit the script on any error
$ErrorActionPreference = "Stop"

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

# Create the droplet and capture the output
Write-Host "Creating Droplet: $DropletName in region $RegionCode with size $Size and image $Image"


$DropletId = C:\WINDOWS\system32\config\systemprofile\doctl\doctl.exe compute droplet create $DropletName --size $Size --image $Image --region $RegionCode  --user-data '#cloud-config
password: KHALIL123er
chpasswd: { expire: False }
ssh_pwauth: True
runcmd:
  - ufw allow 22/tcp
' --format ID --no-header --wait


if (-not $DropletId) {
    Write-Host "Failed to create droplet."
    exit 1
}

# Store the Droplet ID in a temporary file for later use
$TempFile = "$env:TEMP\droplet_id.txt"
Set-Content -Path $TempFile -Value $DropletId

Write-Host "Droplet $DropletName created with ID: $DropletId"