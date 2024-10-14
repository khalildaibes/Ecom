# Parameters that can be passed to the script
param (
    [string]$hostname = "khai"  # Path to the sanity executable

)


# Use Start-Process to run sanity deploy and redirect the input
$deployProcess = Start-Process 'C:\Users\Admin\AppData\Roaming\npm\sanity.cmd' -ArgumentList 'deploy' -WorkingDirectory 'D:\ecommerce\react-ecommerce-website-stripe\sanity-ecommerce-stripe' -NoNewWindow -RedirectStandardInput "D:\Ecom\Ecom\ecommerce\common\api\sanity\input.txt" -PassThru

# Send the hostname to the deploy process
$deployProcess.StandardInput.WriteLine($hostname)
$deployProcess.StandardInput.Close()

# Wait for the process to complete
$deployProcess.WaitForExit()

# Check the exit code
if ($deployProcess.ExitCode -eq 0) {
    Write-Host "Sanity project deployed successfully."
} else {
    Write-Host "Sanity deploy failed with exit code $($deployProcess.ExitCode)"
}
