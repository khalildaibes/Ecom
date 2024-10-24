# get_droplet_info.ps1

# Exit the script on any error
$ErrorActionPreference = "Stop"

# Path to the temporary file where the Droplet ID is stored
$TempFile = "$env:TEMP\droplet_id.txt"

# Read the Droplet ID from the file
if (-not (Test-Path -Path $TempFile)) {
    Write-Host "Droplet ID file not found. Cannot retrieve Droplet information."
    exit 1
}

$DropletId = Get-Content -Path $TempFile

if ([string]::IsNullOrEmpty($DropletId)) {
    Write-Host "Droplet ID not found. Cannot retrieve Droplet information."
    exit 1
}

# Get Droplet info in JSON format
$DropletInfo = C:\WINDOWS\system32\config\systemprofile\doctl\doctl.exe compute droplet get $DropletId --format ID,Name,PublicIPv4,Region,Memory,VCPUs,Disk,Image --no-header --output json

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to retrieve Droplet information."
    exit 1
}




Write-Host "DROPLET_INFO: $DropletInfo"
