import argparse
import sys
import requests
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from ecommerce.common.api.github.gitManager import GitManager
from ecommerce.common.api.jenkins.jenkinsManager import JenkinsManager
from ecommerce.common.api.sanity.saintyManager import SanityManager
from ecommerce.common.api.vercel.vercelManager import VercelManager
from ecommerce.common.helpFunctions.common import load_json_to_dict
#  vercel token vx5yZJY6ksjBgStrtTsRU1lG
# Function to create a Vercel deployment


# Example usage
def trigger_create_config_file_job(params):
    # Jenkins instance details
    jenkins_url = "http://localhost:8080"
    username = "kdaibes"  # Replace with your Jenkins username
    api_token = "Kh6922er!"  # Replace with your Jenkins API token

    # Create an instance of JenkinsManager
    jenkins_manager = JenkinsManager(jenkins_url, username, api_token)

    # Jenkins job to trigger
    job_name = "create_bussniss_config_file"

    # List of keywords to validate in the console output
    keywords = ["Build successful", "Tests passed"]

    # Validate the console output for the last build

    # Jenkins job to trigger


    # Trigger the job and wait for its output
    jenkins_job = jenkins_manager.trigger_and_wait_for_output(job_name, params)

    if jenkins_job:
        print(f"Job Name: {jenkins_job.job_name}")
        print(f"Job URL: {jenkins_job.job_url}")
        print(f"Build Number: {jenkins_job.build_number}")
        print(f"Status: {jenkins_job.status}")
        return jenkins_job
    return None
    

def get_job_params():
            # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate a config JSON file from parameters")
    
    parser.add_argument('--email', required=True, help='Email address')
    parser.add_argument('--password', required=True, help='Password')
    parser.add_argument('--new_business_name', required=True, help='New business name')
    parser.add_argument('--small_description', required=True, help='Small description of the business')
    parser.add_argument('--Template_ID', required=True, help='Template ID')
    parser.add_argument('--categories', required=True, help='Categories (comma-separated)')
    parser.add_argument('--logo_file', required=True, help='Logo image file path')
    parser.add_argument('--phone', required=True, help='Business phone number')
    parser.add_argument('--address', required=True, help='Business address')
    parser.add_argument('--products_file', required=False, help='Products file path (CSV or Excel)')
    parser.add_argument('--location_in_waze', required=False, help='Location in Waze (optional)')
    parser.add_argument('--css_file', required=False, help='CSS file path (optional)')
    parser.add_argument('--banner_photo', required=False, help='Banner photo path (optional)')

    return  parser.parse_args()


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



def main():
    
    
    args = get_job_params()

    config_create_job = trigger_create_config_file_job(vars(args))
    if config_create_job:
        
        project_name = args.new_business_name  # Name of the Vercel project
        project_directory = r"D:\ecommerce\react-ecommerce-website-stripe"
        github_username = "khalildaibes1"
        access_token = os.getenv("VERCELTOKEN")  # Store the token securely as an environment variable
        # Get the directory of the current script
        script_directory = os.path.dirname(os.path.abspath(__file__))
        git_manager = GitManager(project_directory, github_username, os.getenv("GITHUB_TOKEN"))
        # Define the output config JSON file path in the script's directory
        client_config_file = os.path.join(script_directory, f"{project_name}_config.json")
        client_data_dict = load_json_to_dict(client_config_file)

        if client_data_dict:
            print("JSON loaded successfully:")
            print(client_data_dict)
        else:
            print("Failed to load JSON.")
        if not access_token:
            print("Error: Vercel Access Token not found. Please set it as an environment variable.")
            return
                
        
        # Dictionary of placeholders and their corresponding values
        placeholders = {
            "#CLIENT_EMAIL#": client_data_dict.email,
            "#CLIENT_BUSINESS_NAME#": project_name,
            "#CLIENT_PHONE#": client_data_dict.client_phone  # This will not replace the placeholder because the value is False
        }
        # Call the deploy function
        sanity_project_dir = r"D:\ecommerce\react-ecommerce-website-stripe\sanity-ecommerce-stripe"  # Change this to your Sanity project folder

        sanity_token = os.getenv("SANITY_ADMIN_TOKEN")  # Provide your Sanity admin token here

        manager = SanityManager(sanity_project_dir, sanity_token)

        # Steps to initialize and deploy a Sanity project
        manager.change_to_project_dir()  # Change to the Sanity project folder
        manager.sanity_init()  # Initialize the Sanity project
        manager.create_sanity_studio(project_name)  # Create the Sanity Studio
        manager.sanity_deploy()  # Deploy the Sanity project
        manager.extract_project_details()  # Extract the Project ID and Dataset

        # Generate the necessary variables for the environment
        sanity_vars = manager.get_sanity_variables()
        print(sanity_vars)
        os.chdir(project_directory)

        replace_placeholders_in_repo(repo_path=project_directory, placeholders=placeholders, )

        # Call the deploy function
        manager = VercelManager(
                project_name="maisamstore",
                github_username="khalildaibes",
                github_token= os.getenv("GITHUB_TOKEN"),
                vercel_token=os.getenv("VercelToken")
            )

        # Steps to initialize, link, and deploy a project
        manager.init_vercel_project()  # Initialize the Vercel project
        manager.link_vercel_project()  # Link the Vercel project
        manager.deploy_vercel()  # Deploy to Vercel

if __name__ == "__main__":
    main()
