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

    # Run the vercel env add command
    $command = "echo -n '$value' | vercel env add $key production"
    Invoke-Expression $command

    $command = "echo -n '$value' | vercel env add $key development"
    Invoke-Expression $command
}
