import subprocess
import os


class CommandExecutor:
    def __init__(self, vercel_token, digital_ocean_token, github_token, sanity_token, project_root):
        self.vercel_token = vercel_token
        self.digital_ocean_token = digital_ocean_token
        self.github_token = github_token
        self.sanity_token = sanity_token
        self.project_root = project_root

    def run_command(self, command, timeout=300):
        """Run a shell command using subprocess.Popen without shell=True."""
        try:
            # Run the command
            result = subprocess.run(command, capture_output=True, text=True)
            proc = subprocess.Popen(
                command,
                cwd=self.project_root,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True  # ensures string-based input\output (text mode)
            )

            # Providing the input to select the first option (replace '1' with the appropriate index for your case)
            output, error = proc.communicate(input="1\n")

            # Check for any output or errors
            print("Output:", output)
            print("Error:", error)

            # Output the result to console
            print(result.stdout)
            if result.returncode != 0:
                print(f"Error occurred: {result.stderr}")
        except Exception as e:
            print(f"Failed to run PowerShell script: {str(e)}")

    def install_dependencies(self):
        """Install required dependencies using a .bat script."""
        command = ['powershell.exe', "-ExecutionPolicy", "Bypass", "-File",
                   os.path.join(self.project_root, r'ecommerce\common\api\digitalOcean\install_doctl.ps1')]
        return self.run_command(command)

    def authenticate_digital_ocean(self):
        """Authenticate with DigitalOcean using a PowerShell script."""

        command = ['powershell.exe', "-ExecutionPolicy", "Bypass", "-File", os.path.join(self.project_root, r'ecommerce\common\api\digitalOcean\authenticate_doctl.ps1'),
                   '--token', self.digital_ocean_token]
        return self.run_command(command)

    def create_project(self, project_name):
        """Create a new DigitalOcean project using a PowerShell script."""
        command = ['powershell.exe', os.path.join(self.project_root, r'ecommerce\common\api\digitalOcean\create_project.ps1'), project_name]
        return self.run_command(command)

    def create_droplet(self, droplet_name, region, droplet_size, image):
        """Create a DigitalOcean droplet using a PowerShell script."""
        command = ['powershell.exe', os.path.join(self.project_root, r'ecommerce\common\api\digitalOcean\create_droplet.ps1'),
                   droplet_name, region, droplet_size, image]
        return self.run_command(command)

    def get_droplet_info(self, droplet_name):
        """Retrieve and print droplet info using a PowerShell script."""
        command = ['powershell.exe', os.path.join(self.project_root, r'ecommerce\common\api\digitalOcean\get_droplet_info.ps1'),
                   droplet_name]
        return self.run_command(command)


if __name__ == '__main__':
    # Replace these values with the actual tokens and project root
    vercel_token = os.getenv('VERCEL_TOKEN')
    digital_ocean_token = os.getenv('DO_TOKEN')
    github_token = os.getenv('GITHUB_TOKEN')
    sanity_token = os.getenv('SANITY_AUTH_TOKEN')
    project_root = os.getenv("WORKSPACE")


    executor = CommandExecutor(vercel_token, digital_ocean_token, github_token, sanity_token, project_root)

    # Execute tasks based on requirements
    if not executor.install_dependencies():
        print("Failed to install dependencies.")
        exit(1)

    if not executor.authenticate_digital_ocean():
        print("Failed to authenticate with DigitalOcean.")
        exit(1)

    project_name = os.getenv('PROJECT_NAME', 'MyProject')
    if not executor.create_project(project_name):
        print(f"Failed to create project: {project_name}")
        exit(1)

    droplet_name = os.getenv('DROPLET_NAME', 'example-droplet')
    region = os.getenv('REGION', 'New York')
    droplet_size = os.getenv('DROPLET_SIZE', 's-2vcpu-2gb')
    image = os.getenv('IMAGE', 'ubuntu-20-04-x64')

    if not executor.create_droplet(droplet_name, region, droplet_size, image):
        print(f"Failed to create droplet: {droplet_name}")
        exit(1)

    if not executor.get_droplet_info(droplet_name):
        print(f"Failed to retrieve info for droplet: {droplet_name}")
        exit(1)
