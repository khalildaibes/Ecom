# Change to the working directory
Set-Location "D:\ecommerce\react-ecommerce-website-stripe"

# Define the path to your JSON file
$jsonFilePath = "D:\ecommerce\react-ecommerce-website-stripe\vercel_env.json"  # Ensure the correct path is used

# Load the JSON file and iterate over its entries
$jsonData = Get-Content $jsonFilePath | ConvertFrom-Json

# Iterate over each key-value pair in the JSON
foreach ($entry in $jsonData.PSObject.Properties) {
    $key = $entry.Name
    $value = $entry.Value
    # Retrieve the VERCEL_TOKEN environment variable
    $vercelToken = $env:VERCEL_TOKEN

    # Check if it's set
    if ($null -eq $vercelToken) {
        echo "VERCEL_TOKEN is not set."
    } else {
        echo "VERCEL_TOKEN is: $vercelToken"
    }
    # Run the vercel env add command
    $command = "echo -n '$value' | vercel env add $key production --token '$vercelToken'"
    Invoke-Expression $command

    $command = "echo -n '$value' | vercel env add $key development --token '$vercelToken'"
    Invoke-Expression $command
}
