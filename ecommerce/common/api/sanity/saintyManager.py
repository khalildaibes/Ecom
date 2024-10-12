import subprocess
import os
import json
import requests

class SanityManager:
    def __init__(self, sanity_project_dir, sanity_token):
        """
        Initializes the SanityManager.
        
        :param sanity_project_dir: The absolute path to the Sanity project folder.
        :param sanity_token: The token to authenticate against the Sanity API.
        """
        self.sanity_project_dir = sanity_project_dir
        self.sanity_token = sanity_token
        self.sanity_project_id = None
        self.sanity_dataset = None
        self.api_url = "https://api.sanity.io/v1"

    def change_to_project_dir(self):
        """Changes the working directory to the Sanity project folder."""
        try:
            os.chdir(self.sanity_project_dir)
            print(f"Changed directory to {self.sanity_project_dir}")
        except Exception as e:
            print(f"Error changing directory: {e}")

    def sanity_init(self):
        """Initializes a Sanity project by running 'sanity init'."""
        try:
            print("Initializing Sanity project...")
            subprocess.run(['sanity', 'init'], check=True)
            print("Sanity project initialized successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error initializing Sanity project: {e}")

    def sanity_deploy(self):
        """Deploys the Sanity project by running 'sanity deploy'."""
        try:
            print("Deploying Sanity project...")
            subprocess.run(['sanity', 'deploy'], check=True)
            print("Sanity project deployed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error deploying Sanity project: {e}")

    def create_sanity_studio(self, project_name):
        """
        Creates a Sanity Studio in a subdirectory inside the project.
        
        :param project_name: The name of the project, used as a folder name for the Studio.
        """
        try:
            studio_dir = os.path.join(self.sanity_project_dir, project_name, "sanity", "studio")
            
            if not os.path.exists(studio_dir):
                os.makedirs(studio_dir)
                print(f"Created Sanity Studio directory at {studio_dir}")
            else:
                print(f"Sanity Studio directory already exists at {studio_dir}")
                
            # Change to the studio directory
            os.chdir(studio_dir)

            # Initialize the Sanity Studio in the created directory
            print("Initializing Sanity Studio...")
            subprocess.run(['sanity', 'init'], check=True)
            print("Sanity Studio initialized successfully.")
        except Exception as e:
            print(f"Error creating Sanity Studio: {e}")

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
            return None

    def create_sanity_token(self, token_name):
        """
        Creates a new token for Sanity using the API.
        :param token_name: A label for the token.
        :return: The generated token or an error message.
        """
        headers = {
            "Authorization": f"Bearer {self.sanity_token}",
            "Content-Type": "application/json"
        }
        
        token_payload = {
            "name": token_name,
            "permissions": ["read", "write"]
        }

        try:
            response = requests.post(f"{self.api_url}/users/me/tokens", headers=headers, json=token_payload)
            
            if response.status_code == 200:
                new_token = response.json().get("token")
                print(f"Generated token: {new_token}")
                return new_token
            else:
                print(f"Error creating token. Status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"An error occurred while creating the token: {e}")
            return None

    def get_sanity_variables(self):
        """
        Retrieves the necessary environment variables for Sanity.
        :return: A dictionary containing the necessary environment variables.
        """
        sanity_token = self.create_sanity_token(token_name="Project Deployment Token")
        
        return {
            "NEXT_PUBLIC_SANITY_PROJECT_ID": self.sanity_project_id,
            "NEXT_PUBLIC_SANITY_DATASET": self.sanity_dataset,
            "NEXT_PUBLIC_SANITY_TOKEN": sanity_token
        }
