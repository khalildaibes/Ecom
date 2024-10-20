# create_project.ps1
param (
    [string]$ProjectName
)

# Exit the script on any error
$ErrorActionPreference = "Stop"

# Create the project
Write-Host "Creating DigitalOcean project: $ProjectName"
C:\WINDOWS\system32\config\systemprofile\doctl\doctl.exe projects create --name $ProjectName --purpose "Frontend development"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to create project."
    exit 1
}

Write-Host "Project $ProjectName created successfully."
