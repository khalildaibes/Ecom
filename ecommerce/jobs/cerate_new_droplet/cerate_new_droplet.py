import argparse
import subprocess
import os
from typing import re
import logging
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CommandExecutor:
    def __init__(self, digital_ocean_token, project_root):
        self.digital_ocean_token = digital_ocean_token
        self.project_root = project_root

    def run_powershell_command(self, script_path, additional_args=None, input_data=None):
        """Run a PowerShell script with additional arguments and optional input."""
        command = ['powershell.exe', "-ExecutionPolicy", "Bypass", "-NonInteractive", "-File", script_path]

        if additional_args:
            command.extend(additional_args)

        try:
            proc = subprocess.Popen(
                command,
                cwd=self.project_root,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True  # Ensure text-based input/output
            )
            output, error = proc.communicate(input=input_data)

            # Output the result to console
            logger.info(f"Output from {str(script_path)}:\n {str(output)} \n" )
            if error:
                logger.info(f"Error from {str(script_path)}:\n {str(error)}\n")

            if proc.returncode != 0:
                raise Exception(f"Command failed: {error}")

            return output, error
        except Exception as e:
            logger.info(f"Failed to run PowerShell script: {str(e)}")
            return None, str(e)

    def install_doctl(self):
        """Install required dependencies using PowerShell."""
        script_path = os.path.join(self.project_root, r'ecommerce\common\api\digitalOcean\install_doctl.ps1')
        output, error = self.run_powershell_command(script_path)
        if error:
            logger.info("Install doctl failed, but continuing...")
        return output, error

    def authenticate_digital_ocean(self):
        """Authenticate with DigitalOcean using a PowerShell script."""
        script_path = os.path.join(self.project_root, r'ecommerce\common\api\digitalOcean\authenticate_doctl.ps1')
        result = subprocess.run(["C:\WINDOWS\system32\config\systemprofile\doctl\doctl.exe",
                                 'auth', 'init', '--access-token', self.digital_ocean_token],
                                cwd=self.project_root,
                                capture_output=True,
                                text=True
                                )
        if result.stdout:
            # Remove ANSI escape codes for color
            output = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', result.stdout)
            logger.info(output)

        logger.info(f" self.digital_ocean_token:{ self.digital_ocean_token}")
        logger.info(f"Raw Output:{result.stdout}")


    def create_droplet(self, droplet_name, region, size, image):
        """Create a DigitalOcean droplet using PowerShell."""
        script_path = os.path.join(self.project_root, r'ecommerce\common\api\digitalOcean\create_droplet.ps1')
        public_key_path = r"C:\Users\Admin\.ssh\id_ed25519.pub"
        # Check if public_key_path is valid
        if not os.path.exists(public_key_path):
            logger.info(f"Error: Public key file not found at {public_key_path}")
            return
        output, error = self.run_powershell_command(
            script_path, additional_args=[droplet_name, region, size, image, public_key_path]
        )

        if error:
            logger.info(f"Failed to create droplet info. Exiting. with error {error}")
            exit(1)
        return output, error

    def get_droplet_info(self):
        """Retrieve and print droplet info using PowerShell."""
        script_path = os.path.join(self.project_root, r'ecommerce\common\api\digitalOcean\get_droplet_info.ps1')
        output, error = self.run_powershell_command(script_path)
        logger.info(f"DROPLET_RESULT{output}DROPLET_RESULT")
        if error:
            logger.info(f"Failed to retrieve droplet info. Exiting. with error {error}")
            exit(1)
        return output, error


if __name__ == '__main__':
    # Replace these values with the actual tokens and project root
    digital_ocean_token = os.getenv("DIGITAL_OCEAN_TOKEN")
    project_root = "D:\Ecom\Ecom"

    # Create an executor instance
    executor = CommandExecutor(digital_ocean_token, project_root)

    # Execute the blocks one by one
    # executor.install_doctl()  # This can fail, but we will continue regardless

    executor.authenticate_digital_ocean()  # If this fails, the script will exit
    parser = argparse.ArgumentParser(description="Generate a config JSON file from parameters")

    parser.add_argument('--project_name', required=True, help='project name')
    parser.add_argument('--droplet_name', required=True, help='droplet_name')
    parser.add_argument('--region', required=True, help='region')
    parser.add_argument('--droplet_size', required=True, help='droplet_size')
    parser.add_argument('--image', required=True, help='image')


    args = parser.parse_args()
    # Create Droplet (replace with actual values)
    project_name = args.project_name
    droplet_name = args.droplet_name
    region = args.region
    size = args.droplet_size
    image = args.image

    executor.create_droplet(droplet_name, region, size, image)  # If this fails, the script will exit

    executor.get_droplet_info()  # If this fails, the script will exit


