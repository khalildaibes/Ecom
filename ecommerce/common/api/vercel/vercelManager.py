import subprocess
import os
import json
import requests

class VercelManager:
    def __init__(self, project_name, github_username, github_token=None, vercel_token=None):
        self.project_name = project_name
        self.github_username = github_username
        self.vercel_token = vercel_token or os.getenv("VERCEL_TOKEN")
        self.repo_url = f"https://{self.github_username}:{github_token}@github.com/{self.github_username}/{self.project_name}.git"

    def init_vercel_project(self):
        """Initializes a Vercel project."""
        try:
            print("Initializing Vercel project...")
            subprocess.run(['vercel', 'init', self.project_name], check=True)
            print(f"Vercel project {self.project_name} initialized.")
        except subprocess.CalledProcessError as e:
            print(f"Error initializing Vercel project: {e}")

    def link_vercel_project(self):
        """Links the local project with Vercel."""
        try:
            print("Linking Vercel project...")
            subprocess.run(['vercel', 'link'], check=True)
            print("Project linked to Vercel.")
        except subprocess.CalledProcessError as e:
            print(f"Error linking Vercel project: {e}")

    def deploy_vercel(self):
        """Deploys the project to Vercel."""
        try:
            print("Deploying to Vercel...")
            subprocess.run(['vercel', '--prod'], check=True)
            print(f"Project {self.project_name} deployed to Vercel.")
        except subprocess.CalledProcessError as e:
            print(f"Error deploying project to Vercel: {e}")

    def deploy_to_vercel_via_api(self, sanity_project_id, dataset):
        """Deploy the project using Vercel's API."""
        vercel_api_url = "https://api.vercel.com/v13/deployments"
        headers = {
            "Authorization": f"Bearer {self.vercel_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "name": self.project_name,
            "gitSource": {
                "type": "github",
                "repo": self.repo_url,
                "ref": "main"  # You can specify the branch here
            },
            "target": "production",
            "env": {
                "NEXT_PUBLIC_SANITY_PROJECT_ID": sanity_project_id,
                "NEXT_PUBLIC_SANITY_DATASET": dataset,
                # Add other environment variables
            },
        }

        try:
            response = requests.post(vercel_api_url, headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                deployment_info = response.json()
                print(f"Deployment initiated successfully: {deployment_info['url']}")
            else:
                print(f"Error: {response.status_code}, {response.json()}")
        except Exception as e:
            print(f"An error occurred: {e}")


