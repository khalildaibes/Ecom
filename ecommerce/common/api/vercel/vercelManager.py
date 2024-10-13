import subprocess
import os
import json
import requests

class VercelManager:
    def __init__(self, project_root, project_name, github_username, github_token=None, vercel_token=None):
        self.project_name = project_name
        self.project_root = project_root
        self.github_username = github_username
        self.vercel_token = vercel_token or os.getenv("VERCEL_TOKEN")
        self.repo_url = f"https://{self.github_username}:{github_token}@github.com/{self.github_username}/{self.project_name}.git"
        self.vercel_path = r'C:\\Users\\Admin\\AppData\\Roaming\\npm\\vercel.cmd'

    def init_vercel_project(self):
        """Initializes a Vercel project."""
        try:
            print("Initializing Vercel project...")
            subprocess.run([self.vercel_path, 'init','nextjs', self.project_name, '--force'], check=True, cwd= self.project_root)
            print(f"Vercel project {self.project_name} initialized.")
        except subprocess.CalledProcessError as e:
            print(f"Error initializing Vercel project: {e}")

    def link_vercel_project(self):
        """Links the local project with Vercel."""
        try:
            print("Linking Vercel project...")
            subprocess.run([self.vercel_path, 'link','--yes', '--token', self.vercel_token, '--project', str(self.project_name).lower()], check=True
                           , cwd= self.project_root)
            print("Project linked to Vercel.")
        except subprocess.CalledProcessError as e:
            print(f"Error linking Vercel project: {e}")

    def deploy_vercel(self):
        """Deploys the project to Vercel."""
        try:
            verce_json_path = f"{self.project_root}\\vercel.json"
            print("Deploying to Vercel...")
            with open(verce_json_path, 'w') as f:
                f.write("""{"buildCommand": "npm run build",
                  "installCommand": "npm install --legacy-peer-deps" }""")
            powershell_script_path = r"D:\Ecom\Ecom\ecommerce\common\api\vercel\system_enviroment_varibles.ps1"
            subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", powershell_script_path],
                           check=True)
            command = [self.vercel_path, 'git', 'connect', '--token', self.vercel_token]

            # Use subprocess.Popen to handle the interactive prompt
            proc = subprocess.Popen(
                command,
                cwd=self.project_root,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True  # ensures string-based input/output (text mode)
            )

            # Providing the input to select the first option (replace '1' with the appropriate index for your case)
            output, error = proc.communicate(input="1\n")

            # Check for any output or errors
            print("Output:", output)
            print("Error:", error)

            # Ensure the process completes successfully
            if proc.returncode == 0:
                print("Vercel project connected successfully.")
            else:
                print(f"Error occurred: {error}")
            subprocess.run([self.vercel_path, '--prod', '--token', self.vercel_token], check=True
                           , cwd= self.project_root)

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


