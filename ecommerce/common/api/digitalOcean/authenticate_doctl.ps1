# authenticate_doctl.ps1

# Use the provided DigitalOcean token to authenticate
C:\WINDOWS\system32\config\systemprofile\doctl\doctl.exe auth init --access-token $args[0]
