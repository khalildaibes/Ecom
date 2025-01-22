import subprocess
import os
import json
import requests
import re
from shlex import quote as shlex_quote
import logging
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SanityManager:
    def __init__(self, sanity_project_dir):
        """
        Initializes the SanityManager.
        :param sanity_project_dir: The absolute path to the Sanity project folder.
        """
        self.sanity_project_dir = sanity_project_dir
        self.sanity_project_id = None
        self.sanity_dataset = None
        self.sanity_executable = r"C:\Users\Admin\AppData\Roaming\npm\sanity.cmd"
        self.api_url = "https://api.sanity.io/v1"
        # os.environ["SANITY_AUTH_TOKEN"] = self.sanity_token

    def check_sanity_version_conflict(self):
        """Check for conflicting Sanity versions and fix them."""
        try:
            logger.info("Sanity satrt11")
            # Check if both versions are installed
            result = subprocess.run(
                [
                    self.sanity_executable,
                    '--version'
                ],
                capture_output=True,
                text=True
            )
            logger.info("Sanity satrt12")

            sanity_version = result.stdout.strip()
            logger.info(f"Sanity Version: {sanity_version}")
        except subprocess.CalledProcessError as e:
            logger.info(f"Error checking Sanity version: {e}")
            return

        # Remove conflicting Sanity versions based on the output
        if 'v2' in sanity_version and '@sanity/core' in sanity_version:
            logger.info("Sanity V2 and V3 conflict detected. Fixing it...")
            subprocess.run(['npm', 'uninstall', 'sanity'], cwd=self.sanity_project_dir, check=True)
        elif 'v3' in sanity_version and 'sanity' in sanity_version:
            print("Sanity V2 installed with V3 project. Fixing it...")
            subprocess.run(['npm', 'uninstall', '@sanity/core'], cwd=self.sanity_project_dir, check=True)

    def run_powershell_script(self, project_name):


        # Construct the PowerShell command
        command = f'{self.sanity_executable} init -y --create-project {project_name}  --dataset prod --output-path {self.sanity_project_dir}'

        try:
            # Run the command
            result = subprocess.run(command, capture_output=True, text=True)
            proc = subprocess.Popen(
                command,
                cwd=self.sanity_project_dir,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True  # ensures string-based input/output (text mode)
            )

            # Providing the input to select the first option (replace '1' with the appropriate index for your case)
            output, error = proc.communicate(input="1\n")

            # Check for any output or errors
            logger.info("Output:", output)
            logger.info("Error:", error)

            # Output the result to console
            logger.info(result.stdout)
            if result.returncode != 0:
                logger.info(f"Error occurred: {result.stderr}")
        except Exception as e:
            logger.info(f"Failed to run PowerShell script: {str(e)}")



    def sanity_init(self, sanity_project_name):
        """Initializes a Sanity project by running 'sanity init'."""
        try:
            logger.info("Initializing Sanity project...")
            # Check if the directory exists
            if os.path.exists(self.sanity_project_dir):
                # Ensure sanity is installed and init project

                # subprocess.run([self.sanity_executable, 'init', '-y',
                #                 '--create-project', sanity_project_name,
                #                 '--dataset', "prod",
                #                 '--output-path', self.sanity_project_dir],
                #                cwd=self.sanity_project_dir)
                # log_file_path = r'C:\ProgramData\Jenkins\.jenkins\workspace\Deploy_new_ecommerce_website\ecommerce\jobs\create_from_template\sanity_init_output.txt'
                #
                # # Check if the log file exists, if not, create it
                # if not os.path.exists(log_file_path):
                #     with open(log_file_path, 'w') as log_file:
                #         log_file.write('')  # Create an empty log file

                # Command to be executed
                # SANITY_AUTH_TOKEN = os.getenv("SANITY_AUTH_TOKEN")
                # sanity_command = f'{self.sanity_executable} init -y --create-project {sanity_project_name} --with-user-token {SANITY_AUTH_TOKEN} --dataset prod --output-path {self.sanity_project_dir}  > {log_file_path} 2>&1'

                self.run_powershell_script(project_name=sanity_project_name)


                logger.info("Sanity project initialized successfully.")
            else:
                logger.info(f"Directory not found: {self.sanity_project_dir}")
        except subprocess.CalledProcessError as e:
            logger.info(f"Error initializing Sanity project: {e}")

    def sanity_deploy(self, project_name:str ):
        """Deploys the Sanity project by running 'sanity deploy'."""
        try:

            print("Deploying Sanity project...")

            # Path to your PowerShell script
            powershell_script_path = r'D:\Ecom\Ecom\ecommerce\common\api\sanity\deploy_sanity.ps1'
            powershell_input_path = r'D:\Ecom\Ecom\ecommerce\common\api\sanity\input.txt'
            with open(powershell_input_path, 'r') as f:
                content = f.read()

            updated_content = content
            updated_content.replace("#PROJECT_STUDIO_HOST#",project_name )
            if updated_content != content:
                with open(powershell_input_path, 'w') as f:
                    f.write(updated_content)
                print(f"Replaced placeholder PROJECT_STUDIO_HOST in {powershell_input_path}")

            # Running the PowerShell script using subprocess
            subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", powershell_script_path],
                               check=True)
            print("PowerShell script ran successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error deploying Sanity project: {e}")

    def extract_project_details(self):
        """Extracts project ID and dataset from the sanity.json file."""
        sanity_config_file = os.path.join(self.sanity_project_dir, 'sanity.json')
        if os.path.exists(sanity_config_file):
            with open(sanity_config_file, 'r') as file:
                config_data = json.load(file)
                self.sanity_project_id = config_data['api'].get('projectId')
                self.sanity_dataset = config_data['api'].get('dataset')
                print(f"Sanity Project ID: {self.sanity_project_id}")
                print(f"Sanity Dataset: {self.sanity_dataset}")
        else:
            print(f"Error: {sanity_config_file} not found.")

    # def create_sanity_token(self, token_name):
    #     """Creates a new token for Sanity using the API."""
    #     headers = {
    #         "Authorization": f"Bearer {self.sanity_token}",
    #         "Content-Type": "application/json"
    #     }
    #     token_payload = {
    #         "name": token_name,
    #         "permissions": ["read", "write"]
    #     }
    #
    #     try:
    #         response = requests.post(f"{self.api_url}/users/me/tokens", headers=headers, json=token_payload)
    #         if response.status_code == 200:
    #             new_token = response.json().get("token")
    #             print(f"Generated token: {new_token}")
    #             return new_token
    #         else:
    #             print(f"Error creating token. Status code: {response.status_code}")
    #     except Exception as e:
    #         print(f"An error occurred while creating the token: {e}")
    def run_powershell_command(self,command):
        """
        Run a PowerShell command and capture its output.

        :param command: The PowerShell command to run.
        :return: The standard output of the command.
        """
        try:
            # Run the PowerShell command
            result = subprocess.run([command], capture_output=True, text=True, check=True)

            # Return the standard output
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {e}")
            return None

    def parse_sanity_output(self, output):
        """
        Parse the 'sanity debug --secrets' command output to extract useful information.

        :param output: The output string from the 'sanity debug --secrets' command.
        :return: A dictionary with parsed information.
        """
        parsed_data = {}
        user_id = re.search(r"ID:\s+'(.*?)'", output)
        user_name = re.search(r"Name:\s+'(.*?)'", output)
        user_email = re.search(r"Email:\s+'(.*?)'", output)
        user_roles = re.search(r"Roles:\s+\[\s+'(.*?)'\s+\]", output)
        project_name = re.search(r"Display name:\s+'(.*?)'", output)
        # Example parsing using regex to extract 'Auth token', 'Project ID', 'Studio URL', etc.
        auth_token = re.search(r"Auth token: '(.*?)'", output)
        project_id = re.search(r"Project:\s+ID:\s+'(.*?)'", output)
        studio_url = re.search(r"Studio URL: '(.*?)'", output)

        if auth_token:
            parsed_data['auth_token'] = auth_token.group(1)
        if project_id:
            parsed_data['project_id'] = project_id.group(1)
        if studio_url:
            parsed_data['studio_url'] = studio_url.group(1)
        if project_name:
            parsed_data['project_name'] = project_name.group(1)

        return parsed_data

    def get_sanity_variables(self):
        """Retrieves the necessary environment variables for Sanity."""
        # Run the PowerShell command
        result = subprocess.run([self.sanity_executable,
                                 '--auth', os.getenv('SANITY_AUTH_TOKEN'),
                                 'debug', '--secrets'],
                                cwd=self.sanity_project_dir,
                                capture_output=True,
                                text=True
                                )

        if result.stdout:
            print("Raw Output:")
            # Remove ANSI escape codes for color
            output = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', result.stdout)
            print(output)



            # Parse the output
            parsed_info = self.parse_sanity_output(output)
            print("\nParsed Information:")
            print(parsed_info)
            return {
                "NEXT_PUBLIC_SANITY_PROJECT_ID": parsed_info['project_id'],
                "NEXT_PUBLIC_SANITY_DATASET": "prod",
                "NEXT_PUBLIC_SANITY_TOKEN": parsed_info['auth_token']
            }
        else:
            print("Failed to run the command.")


    def extract_auth_token(self,command_output):
        """
        Extracts the Auth token from the command output.

        :param command_output: The string containing the command output.
        :return: The extracted Auth token or None if not found.
        """
        # Regular expression to match the Auth token line
        auth_token_pattern = re.compile(r"Auth token:\s*'(.*?)'")

        # Search for the Auth token in the command output
        match = auth_token_pattern.search(command_output)

        if match:
            # Return the Auth token if found
            return match.group(1)
        else:
            print("Auth token not found in the command output.")
            return None