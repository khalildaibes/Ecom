# Parameters that can be passed to the script
param (
    [string]$sanityExecutable = "C:\Users\Admin\AppData\Roaming\npm\sanity.cmd",  # Path to the sanity executable
    [string]$sanityProjectName = "your_project_name",  # The name of the project to create
    [string]$sanityAuthToken = "your_sanity_auth_token",  # Sanity auth token
    [string]$sanityProjectDir = "D:\ecommerce\react-ecommerce-website-stripe\sanity-ecommerce-stripe",  # Project directory
    [string]$logFilePath = "D:\ecommerce\react-ecommerce-website-stripe\sanity_init_output.log"  # Path to the log file
)

# Ensure log file exists
if (-not (Test-Path -Path $logFilePath)) {
    New-Item -Path $logFilePath -ItemType File
}

# Store the input for the sanity command (e.g., for when it prompts for input)
$inputText = "n"  # Set this to 'n' if you want to answer 'No' when prompted

# Build the command for initializing the Sanity project
$sanityCommand = "$sanityExecutable init -y --create-project $sanityProjectName --with-user-token $sanityAuthToken --dataset prod --output-path $sanityProjectDir"

# Write the command to the log file
Add-Content -Path $logFilePath -Value "Running Sanity command: $sanityCommand"

# Start the process and pipe in the input when needed
$deployProcess = Start-Process -FilePath "powershell" `
    -ArgumentList "/c", $sanityCommand `
    -WorkingDirectory $sanityProjectDir `
    -NoNewWindow `
    -RedirectStandardInput $inputText `
    -RedirectStandardOutput $logFilePath `
    -RedirectStandardError $logFilePath `
    -PassThru

# Wait for the process to complete
$deployProcess.WaitForExit()

# Check the exit code
if ($deployProcess.ExitCode -eq 0) {
    Add-Content -Path $logFilePath -Value "Sanity project initialized successfully."
    Write-Host "Sanity project initialized successfully."
} else {
    Add-Content -Path $logFilePath -Value "Sanity initialization failed with exit code $($deployProcess.ExitCode)"
    Write-Host "Sanity initialization failed with exit code $($deployProcess.ExitCode)"
}
