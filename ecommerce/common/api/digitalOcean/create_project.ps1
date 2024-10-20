# create_project.ps1
param (
    [string]$ProjectName
)

# Exit the script on any error
$ErrorActionPreference = "Stop"

# Create the project
Write-Host "Creating DigitalOcean project: $ProjectName"
doctl projects create --name $ProjectName --purpose "Frontend development"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to create project."
    exit 1
}

Write-Host "Project $ProjectName created successfully."
