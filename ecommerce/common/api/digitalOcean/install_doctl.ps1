# # install_doctl.ps1
#
# # Download and install DigitalOcean CLI (doctl) for Windows
# Invoke-WebRequest -Uri https://github.com/digitalocean/doctl/releases/download/v1.115.0/doctl-1.115.0-windows-amd64.zip -OutFile $env:TEMP\doctl.zip
#
# # Unzip the downloaded file
# Expand-Archive -Path $env:TEMP\doctl.zip -DestinationPath $env:USERPROFILE\doctl
#
# # Add doctl to PATH (optional, depending on how you use it)
# $env:PATH += ";$env:USERPROFILE\doctl"
