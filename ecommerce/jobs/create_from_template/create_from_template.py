import argparse
import requests
import os
import json

from ecommerce.common.api.github.gitManager import GitManager
from ecommerce.common.api.jenkins.jenkinsManager import JenkinsManager
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
    job_name = "my-second-pipeline"


    # Trigger the job and wait for its output
    jenkins_job = jenkins_manager.trigger_and_wait_for_output(job_name, params)

    if jenkins_job:
        print(f"Job Name: {jenkins_job.job_name}")
        print(f"Job URL: {jenkins_job.job_url}")
        print(f"Build Number: {jenkins_job.build_number}")
        print(f"Status: {jenkins_job.status}")
        return jenkins_job
    return None
    



def deploy_to_vercel(project_name, access_token, git_repo_url):
    vercel_api_url = "https://api.vercel.com/v13/deployments"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Configuration for deployment
    payload = {
        "name": project_name,
        "gitSource": {
            "type": "github",
            "repo": git_repo_url,
            "ref": project_name  # Specify the branch to deploy
        },
        "target": "production",  # Specify "production" or "staging"
        "env": {
            "NEXT_PUBLIC_SANITY_PROJECT_ID":"albtn5mx",
            "NEXT_PUBLIC_SANITY_DATASET":"dev",
            "NEXT_PUBLIC_SANITY_TOKEN":"sksBN414BGpxNZeBZa9FtElb39FXaCvyBWwnTNzyXBFL1CVcITXhCm1pv0OQh4nAhYkOQDpDCSAjubewxXgrLdKze6AirWavDBi02EaPg4Ahoh5mxgTrJaBQiHIXrCOuvUiUOUrByuZueUOk8136HKhfNgV9sHcPaXjk34oPmME8IV8yDkpX",
            "NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY":"pk_test_51PpVmfRwcVDABXBxzwrzZTGJ4QR627fy1CeV9o3MMrFi5zTz2O1LHr7pqUB2uMQwIBhtqGvuVCGETR1AuO9Iwdbr00TS5IiW8d",
            "NEXT_PUBLIC_STRIPE_SECRET_KEY":"sk_test_51PpVmfRwcVDABXBx2w0Jpm7CsdULO31MMy43ysw8avcB2wqJ6CacLgn73wCwc4kxcaxmFwmEjwqsLQPL9jCcrFXC00YK8LCueg",
            "PHONE_NUMBER_ID" : "209317558942807",
            "WHATSAPP_ACCESS_TOKEN" : 'EAANVrunrZADwBO7r4C0KoWsjkWp0nLIXqFIZCDYbHwFLtieaBgxUQWV3sJC0CZBupVZCG2t5gOFys2SoJfKc6fBrmAPpZCM6sGuBdXeRORYJk9a3VKYVZCRNaHMkKi3fNK7LFjSYW4mdg7Tvn9DVsWMnzv1NFZA1rZCZBysTZCJnQayUuFI9EFh7EQRXYfLpburii4BZCifRw2ibceclhfZA',
        },
    }

    try:
        # Make the API call to deploy the project
        response = requests.post(vercel_api_url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            deployment_info = response.json()
            print("Deployment initiated successfully!")
            print(f"Deployment URL: {deployment_info['url']}")
            print(f"Deployment ID: {deployment_info['id']}")
        else:
            print(f"Error: Failed to deploy. Status code: {response.status_code}")
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

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
    
def main():
    
    
    args = get_job_params()
    config_create_job = trigger_create_config_file_job(args)
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

        # Call the deploy function
        deploy_to_vercel(project_name, access_token, git_manager.get_repo_url())


if __name__ == "__main__":
    main()
