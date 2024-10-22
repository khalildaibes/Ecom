import argparse
import json
import os
import subprocess
import sys
import logging
from datetime import datetime
import re
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from ecommerce.common.api.digitalOcean.run_and_deploy_on_vpc import VpcCommands
from ecommerce.common.api.jenkinsAPI.jenkinsManager import JenkinsManager
from ecommerce.common.api.github.gitManager import GitManager
from ecommerce.common.api.sanity.saintyManager import SanityManager
from ecommerce.common.api.vercel.vercelManager import VercelManager
from ecommerce.common.helpFunctions.common import load_json_to_dict, handle_error

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def trigger_create_config_file_job(params):
    jenkins_manager = JenkinsManager(jenkins_url="http://localhost:8080", username="kdaibes", api_token="Kh6922er!")
    return jenkins_manager.trigger_and_wait_for_output("create_bussniss_config_file", params)

def trigger_create_vpc_in_digital_ocean_job(params):
    jenkins_manager = JenkinsManager(jenkins_url="http://localhost:8080", username="kdaibes", api_token="Kh6922er!")
    return jenkins_manager.trigger_and_wait_for_output("deploy_new_droplet", params)

def get_job_params():
    parser = argparse.ArgumentParser(description="Generate a config JSON file from parameters")
    required_args = ['email', 'password', 'new_business_name', 'new_branch_name', 'small_description', 'Template_ID',
                     'categories', 'logo_file', 'phone', 'address', "db_selected"]
    for arg in required_args:
        parser.add_argument(f'--{arg}', required=True)

    parser.add_argument('--products_file', '--location_in_waze', '--css_file', '--banner_photo', required=False)
    return parser.parse_args()


def replace_placeholders_in_repo(repo_path, placeholders):
    exclude_dirs = ['node_modules', '.next']

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file not in ["package-lock.json", "package-lock.json", "package.json"]:
                if file.endswith(('.txt', '.py', '.html', '.js', '.json', '.md', '.env')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding="UTF-8") as f:
                            content = f.read()

                        updated_content = content
                        for placeholder, replacement in placeholders.items():
                            if replacement:
                                updated_content = updated_content.replace(placeholder, replacement)
                                logger.info(f"Updated {placeholder} with {replacement} in {file_path}")

                        if updated_content != content:
                            with open(file_path, 'w') as f:
                                f.write(updated_content)
                            logger.info(f"Replaced placeholders in {file_path}")
                    except Exception as e:
                        logger.error(f"Error processing {file_path}: {e}")
                        handle_error(e,fail_job=True)

def setup_git_manager(project_directory, github_username):
    return GitManager(project_directory, github_username, os.getenv("GITHUB_TOKEN"))

def deploy_sanity(sanity_project_dir, project_name, args, client_data_dict):
    sanity_token = os.getenv("SANITY_ADMIN_TOKEN")
    manager = SanityManager(sanity_project_dir)
    manager.check_sanity_version_conflict()
    manager.sanity_init(sanity_project_name=args.new_business_name)
    sanity_vars = manager.get_sanity_variables()

    placeholders = {
        'next_public_sanity_project_id_placeholder': sanity_vars['NEXT_PUBLIC_SANITY_PROJECT_ID'],
        'next_public_sanity_dataset_placeholder': sanity_vars['NEXT_PUBLIC_SANITY_DATASET'],
        'next_public_sanity_token_placeholder': sanity_vars['NEXT_PUBLIC_SANITY_TOKEN'],
        '--PHONE_NUMBER_ID--': args.phone,
        "--CLIENT_EMAIL--": client_data_dict.get('email'),
        "client_business_name_placeholder": args.new_business_name,
        "--CLIENT_PHONE--": client_data_dict.get('phone'),
    }
    os.environ['VERCEL_TOKEN'] = sanity_vars['NEXT_PUBLIC_SANITY_TOKEN']

    ecommerce_template_path = r"D:\ecommerce\react-ecommerce-website-stripe"
    vercel_json_path = r"D:\ecommerce\react-ecommerce-website-stripe\vercel_env.json"

    with open(vercel_json_path, 'w') as f:
        json.dump(placeholders, f, indent=4)
    replace_placeholders_in_repo(ecommerce_template_path, placeholders)

    upper_case_placeholders = {key.upper().replace('_PLACEHOLDER', ''): value for key, value in placeholders.items()}
    with open(vercel_json_path, 'w') as f:
        json.dump(upper_case_placeholders, f, indent=4)

    logger.info(f"Vercel environment variables written to {vercel_json_path}")
    return sanity_vars

def deploy_vercel(project_name):
    manager = VercelManager(
        project_root=r"D:\ecommerce\react-ecommerce-website-stripe",
        project_name=project_name,
        github_username="khalildaibes",
        github_token=os.getenv("GITHUB_TOKEN"),
        vercel_token='vx5yZJY6ksjBgStrtTsRU1lG'
    )
    manager.link_vercel_project()
    manager.deploy_vercel()

def checkout_and_create_branch(existing_branch, new_branch, project_directory):
    try:
        github_username = "khalildaibes1"
        git_manager = GitManager(project_directory, github_username, os.getenv("GITHUB_TOKEN"))
        git_manager.checkout_and_create_branch(existing_branch, new_branch)
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: {e}")
        handle_error(e)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        handle_error(e)


def fix_invalid_json(json_string):
    """
    Fixes invalid single backslashes in a JSON string by converting them into double backslashes.
    """
    # Regex pattern to find backslashes that are not part of a valid escape sequence
    # It looks for a single backslash not followed by a valid escape character
    invalid_backslash_pattern = r'(?<!\\)\\(?![bfnrtu"\'])'

    # Replace invalid single backslashes with double backslashes
    return re.sub(invalid_backslash_pattern, r'\\\\', json_string)

def extract_droplet_info(console_output):
    """
    Extracts the JSON array following the first occurrence of 'DROPLET_INFO' from the Jenkins console output.
    """
    # Define a regex pattern to match 'DROPLET_INFO: [ ... ]'
    # Use regex to find the JSON block inside the console output
    match = re.search(r'DROPLET_RESULT(.*?)DROPLET_RESULT', console_output, re.DOTALL)
    if match:
        # Extract the JSON string (array format)
        json_array_str = match.group(1).strip()  # Get the JSON content and strip any extra spaces
        json_array_str = json_array_str.replace("DROPLET_INFO:",'').strip()
        try:
            # Parse the JSON array to convert it into a Python object
            droplet_info = json.loads(json_array_str)
            print("Droplet info extracted successfully.")
            return droplet_info
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            return None
    else:
        print("DROPLET_INFO not found in the console output.")
        return None

def deploy_new_vpc(params):
    try:
        droplet_deploy_jenkins_job_info = trigger_create_vpc_in_digital_ocean_job(params=params)
        # Get the first item of the list as a dictionary
        print (F"deploying VPC jenkins has fainished with satatus {droplet_deploy_jenkins_job_info.status}")
        print (F"deploying VPC jenkins has fainished with console_output {droplet_deploy_jenkins_job_info.console_output}")
        extract_droplet_info_output = droplet_deploy_jenkins_job_info.console_output
        extract_droplet_info_result = extract_droplet_info(extract_droplet_info_output)
        print(f"extract_droplet_info_result is {extract_droplet_info_result}")
        if extract_droplet_info_result:
            first_droplet = extract_droplet_info_result[0]

            # Extract the droplet name
            droplet_name = first_droplet['name']

            # Extract the current timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            # Construct the filename using timestamp and droplet name
            filename = f"{timestamp}_{droplet_name}.txt"



            # Write the output to a file
            with open(filename, 'w') as file:
                file.write(droplet_deploy_jenkins_job_info.console_output)
            logger.info(droplet_deploy_jenkins_job_info.console_output)
            return first_droplet
    except Exception as ex:
        print("Error: failed to resolve the jenkins ")
        handle_error(ex)


def create_and_deploy_stripe_vpc(parameters):
    first_droplet = deploy_new_vpc(params=parameters)
    # Extract the droplet name
    droplet_id = first_droplet['id']
    droplet_name = first_droplet['name']
    public_ip_address = None
    for network in first_droplet['networks']['v4']:
        if network['type'] == 'public':
            public_ip_address = network['ip_address']
            break

    # Prepare the content to write to the file
    if public_ip_address:
        vpc = VpcCommands(ssh_client=public_ip_address)
        vpc.setup_strapi_on_vps(vpc_ip=public_ip_address, droplet_name=droplet_name, username="root",
                                password="KHALIL123er", github_token=os.getenv("GITHUB_TOKEN"))


def run_job():
    args = get_job_params()
    try:
        config_create_job = trigger_create_config_file_job(vars(args))
        if config_create_job:
            existing_branch = 'template_maisam_makeup'
            project_directory = r"D:\ecommerce\react-ecommerce-website-stripe"
            checkout_and_create_branch(existing_branch, f'feature/{args.new_branch_name}', project_directory=project_directory)
            checkout_and_create_branch(existing_branch, f'feature/{args.new_branch_name}', project_directory=f'{project_directory}\sanity-ecommerce-stripe')
            project_name = args.new_branch_name
            client_config_file = f'C:\\ProgramData\\Jenkins\\.jenkins\\workspace\\create_bussniss_config_file\\ecommerce\\jobs\\create_bussniss_config_file\\{project_name}_config.json'
            client_data_dict = load_json_to_dict(client_config_file)

            if client_data_dict:
                logger.info("JSON loaded successfully")
            else:
                logger.error("Failed to load JSON")
                return

            if args.db_selected == "Sanity":
                sanity_vars = deploy_sanity(r"D:\ecommerce\react-ecommerce-website-stripe\sanity-ecommerce-stripe", project_name, args, client_data_dict)
                logger.info(sanity_vars)
            if args.db_selected == "Stripe":
                params = vars(args) | client_data_dict
                create_and_deploy_stripe_vpc(parameters=params)

            deploy_vercel(project_name)
    except Exception as e:
        handle_error(e)

def main():
    try:
        run_job()
    except Exception as e:
        handle_error(e)

if __name__ == "__main__":
    main()
