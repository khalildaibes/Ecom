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

$DropletId = "453613182"

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

# Run the doctl command and automatically send "yes" to the host authenticity prompt

C:\WINDOWS\system32\config\systemprofile\doctl\doctl.exe compute ssh $DropletID --ssh-command "sudo sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config && sudo systemctl restart sshd && sudo ufw allow 22/tcp" --ssh-key-path "C:\Users\Admin\.ssh\id_ed25519" | echo 'yes'

Write-Host "DROPLET_INFO: $DropletInfo"
