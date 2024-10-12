import argparse
import requests
import os
import json

from ecommerce.common.api.github.gitManager import GitManager
from ecommerce.common.api.jenkinsAPI.jenkinsManager import JenkinsManager
from ecommerce.common.api.sanity.saintyManager import SanityManager
from ecommerce.common.helpFunctions.common import load_json_to_dict
from ecommerce.jobs.create_from_template.create_from_template import deploy_to_vercel
#  vercel token vx5yZJY6ksjBgStrtTsRU1lG
# Function to create a Vercel deployment

def replace_placeholders_in_repo(repo_path, placeholders):
    """
    Replace placeholders in the repository files if the corresponding value is provided.
    
    :param repo_path: Path to the repository.
    :param placeholders: Dictionary where keys are placeholders and values are their replacements.
    """
    # Traverse through the repository files
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            
            # Only process text-based files (e.g., .txt, .py, .html, etc.)
            if file.endswith(('.txt', '.py', '.html', '.js', '.json', '.md')):
                try:
                    with open(file_path, 'r') as f:
                        file_content = f.read()

                    # Track if any replacements are made
                    updated_content = file_content
                    
                    # Iterate over the placeholders dictionary and perform replacements
                    for placeholder, replacement in placeholders.items():
                        # If the value is True, replace the placeholder
                        if replacement:
                            updated_content = updated_content.replace(placeholder, replacement)
                    
                    # If the content has been updated, write it back to the file
                    if updated_content != file_content:
                        with open(file_path, 'w') as f:
                            f.write(updated_content)
                        
                        print(f"Replaced placeholders in {file_path}")
                except Exception as e:
                    print(f"An error occurred while processing {file_path}: {str(e)}")

def get_job_params():
            # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate a config JSON file from parameters")
    
    parser.add_argument('--user_config_file', required=True, help='Email address')

    return  parser.parse_args()
    
def main():
    
    
    args = get_job_params()
    if args.user_config_file :
        json_data = load_json_to_dict(args.json_file)
        project_name= json_data.new_business_name
        project_directory = r"D:\ecommerce\react-ecommerce-website-stripe"
        github_username = "khalildaibes1"
        access_token = os.getenv("VERCELTOKEN")  # Store the token securely as an environment variable
        # Get the directory of the current script
        script_directory = os.path.dirname(os.path.abspath(__file__))
        git_manager = GitManager(project_directory, github_username, os.getenv("GITHUB_TOKEN"))
        # Define the output config JSON file path in the script's directory
        git_manager.pull_code_from_git(branch_name=project_name)
        if json_data:
            print("JSON loaded successfully:")
            print(json_data)
        else:
            print("Failed to load JSON.")
        if not access_token:
            print("Error: Vercel Access Token not found. Please set it as an environment variable.")
            return


        
        deploy_to_vercel(project_name, access_token, git_manager.get_repo_url())
            # Set the static path to your Sanity project directory
            



if __name__ == "__main__":
    main()
