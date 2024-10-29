import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from ecommerce.common.api.digitalOcean.run_and_deploy_on_vpc import VpcCommands
from ecommerce.common.api.jenkinsAPI.jenkinsManager import JenkinsManager
from ecommerce.common.helpFunctions.common import handle_error, logger


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
            logger.info("Droplet info extracted successfully.")
            return droplet_info
        except json.JSONDecodeError as e:
            logger.info(f"Failed to parse JSON: {e}")
            return None
    else:
        logger.info("DROPLET_INFO not found in the console output.")
        return None


def sanitize_droplet_name(input_name: str) -> str:
    # Remove all invalid characters (anything that's not a-z, A-Z, 0-9, dots, or hyphens)
    sanitized_name = re.sub(r'[^a-zA-Z0-9.-]', '', input_name)

    # If the name is empty after sanitization, return a default name
    if not sanitized_name:
        return "default-droplet"

    # Limit the name to a reasonable length (e.g., 63 characters)
    sanitized_name = sanitized_name[:63]

    # Ensure it doesn't start or end with a hyphen or dot
    sanitized_name = sanitized_name.strip("-.")

    # If the result is empty after stripping, return a default name
    if not sanitized_name:
        return "default-droplet"

    return sanitized_name

def trigger_create_vpc_in_digital_ocean_job(params):
    jenkins_manager = JenkinsManager(jenkins_url="http://localhost:8080", username="kdaibes", api_token="Kh6922er!")
    jobs_params= {
         "project_name": sanitize_droplet_name(params["new_business_name"]),
         "region": "Frankfurt",
         "droplet_name": sanitize_droplet_name(params["new_business_name"]),
         "droplet_size": "s-2vcpu-2gb",
         "image":"ubuntu-20-04-x64"
                  }
    return jenkins_manager.trigger_and_wait_for_output("deploy_new_droplet", jobs_params)

def deploy_new_vpc(params):
    try:
        droplet_deploy_jenkins_job_info = trigger_create_vpc_in_digital_ocean_job(params=params)
        # Get the first item of the list as a dictionary
        logger.info(F"deploying VPC jenkins has fainished with satatus {droplet_deploy_jenkins_job_info.status}")
        logger.info(F"deploying VPC jenkins has fainished with console_output {droplet_deploy_jenkins_job_info.console_output}")
        extract_droplet_info_output = droplet_deploy_jenkins_job_info.console_output
        extract_droplet_info_result = extract_droplet_info(extract_droplet_info_output)
        logger.info(f"extract_droplet_info_result is {extract_droplet_info_result}")
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
    droplet_name = first_droplet['name']
    public_ip_address = None
    for network in first_droplet['networks']['v4']:
        if network['type'] == 'public':
            public_ip_address = network['ip_address']
            break
    if not public_ip_address:
        print("failed to retrieve ip address.")

    # Prepare the content to write to the file
    vpc = VpcCommands(vpc_ip=public_ip_address, username="root", password="KHALIL123er")
    # Define local and remote file paths
    local_file_path = Path(r"D:\Ecom\Ecom\ecommerce\common\api\digitalOcean\setup_strapi.sh")
    remote_file_path = f"/root/setup_strapi.sh"


    # Copy the script to the server
    vpc.copy_file_to_server(local_file_path, remote_file_path)

    # Run the script on the server
    vpc.run_script_on_server(remote_file_path,public_ip_address,os.getenv("GITHUB_TOKEN"),droplet_name,"KHALIL123er" )


def get_job_params():
    parser = argparse.ArgumentParser(description="Generate a config JSON file from parameters")
    required_args = ['email', 'password', 'new_business_name', 'new_branch_name', 'small_description', 'Template_ID',
                     'categories', 'phone', 'address', "db_selected", 'customer_config_file_path','logo_file ']

    for arg in required_args:
        parser.add_argument(f'--{arg}', required=True)
    parser.add_argument('--products_file', '--location_in_waze', '--css_file', '--banner_photo', required=False)

    return parser.parse_args()


def main():
    args = get_job_params()
    try:
        create_and_deploy_stripe_vpc(parameters=vars(args))
    except Exception as e:
        handle_error(e)

if __name__ == "__main__":
    main()