import subprocess
import os

class GitManager:
    def __init__(self, project_directory, github_username, github_token=None):
        self.project_directory = project_directory
        self.github_username = github_username
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")

        if not self.github_token:
            raise Exception("GitHub token not found. Please set the GITHUB_TOKEN environment variable or pass it to the class.")

    def configure_git_credentials(self):
        """Configure Git to store credentials."""
        print("Configuring Git credential helper to store credentials...")
        subprocess.run(['git', 'config', '--global', 'credential.helper', 'store'], check=True)

    def checkout_and_create_branch(self, existing_branch, new_branch):
        """Checkout to an existing branch and create a new branch."""
        try:
            # Change to the project directory
            os.chdir(self.project_directory)
            print(f"Changed to directory: {os.getcwd()}")

            # Prepare the repository URL with the token
            repo_url = f"https://{self.github_username}:{self.github_token}@github.com/{self.github_username}/maisamstore.git"

            # Configure Git credential helper
            self.configure_git_credentials()

            # Step 1: Checkout the existing branch
            subprocess.run(['git', 'checkout', existing_branch], check=True)
            print(f"Checked out to {existing_branch}")
            
            # Step 2: Create and checkout the new branch
            subprocess.run(['git', 'checkout', '-b', new_branch], check=True)
            print(f"Created and switched to new branch {new_branch}")

            # Step 3: Push the new branch to the remote repository using the token
            subprocess.run(['git', 'push', '-u', repo_url, new_branch], check=True)
            print(f"Pushed {new_branch} to origin and set upstream.")

        except subprocess.CalledProcessError as e:
            print(f"Git command failed: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
