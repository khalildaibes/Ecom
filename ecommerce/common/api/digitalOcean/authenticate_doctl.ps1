# authenticate_doctl.ps1

# Use the provided DigitalOcean token to authenticate
doctl auth init --access-token $args[0]
