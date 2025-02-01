import argparse
import json
import os
import smtplib
import subprocess
import sys
import logging
from datetime import datetime
import re
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
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

def trigger_setup_strapi_job(params):
    jenkins_manager = JenkinsManager(jenkins_url="http://localhost:8080", username="kdaibes", api_token="Kh6922er!")
    return jenkins_manager.trigger_and_wait_for_output("setup_strapi_job", params)

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
    logger.info("Sanity satrt1")

    manager = SanityManager(sanity_project_dir)
    logger.info("Sanity satrt2")

    manager.check_sanity_version_conflict()
    logger.info("Sanity satrt3")

    manager.sanity_init(sanity_project_name=args.new_branch_name)
    logger.info("Sanity satrt4")

    sanity_vars = manager.get_sanity_variables()
    logger.info("Sanity satrt5")

    placeholders = {
        'next_public_sanity_project_id_placeholder': sanity_vars['NEXT_PUBLIC_SANITY_PROJECT_ID'],
        'next_public_sanity_dataset_placeholder': sanity_vars['NEXT_PUBLIC_SANITY_DATASET'],
        'next_public_sanity_token_placeholder': sanity_vars['NEXT_PUBLIC_SANITY_TOKEN'],
        '--PHONE_NUMBER_ID--': args.phone,
        '#background_color#':'ffebf0',
        '#border-color#':'ff4081',
        '#color2#':'e91e63',
        '#color3#':'ff6fae',
        '#color4#':'fedcdb',
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

def deploy_vercel(project_name, branch):
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
        git_manager = GitManager(project_directory, github_username, os.getenv("GITHUB_TOKEN",default=""))
        git_manager.checkout_and_create_branch(existing_branch, new_branch)
        return git_manager
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: {e}")
        handle_error(e)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        handle_error(e,place =" checkout branch")


def fix_invalid_json(json_string):
    """
    Fixes invalid single backslashes in a JSON string by converting them into double backslashes.
    """
    # Regex pattern to find backslashes that are not part of a valid escape sequence
    # It looks for a single backslash not followed by a valid escape character
    invalid_backslash_pattern = r'(?<!\\)\\(?![bfnrtu"\'])'

    # Replace invalid single backslashes with double backslashes
    return re.sub(invalid_backslash_pattern, r'\\\\', json_string)

def run_job():
    args = get_job_params()
    try:
        config_create_job = trigger_create_config_file_job(vars(args))
        existing_branch = 'template_maisam_makeup_strapi'

        if config_create_job:
            if args.db_selected == "Sanity":
                existing_branch = 'template_maisam_makeup'
            if args.db_selected == "Stripe":
                existing_branch = 'template_maisam_makeup_strapi'

            project_directory = r"D:\ecommerce\react-ecommerce-website-stripe"
            project_git_manager = checkout_and_create_branch(existing_branch, f'feature/{args.new_branch_name}', project_directory=project_directory)
            sanity_git_manager =checkout_and_create_branch(existing_branch, f'feature/{args.new_branch_name}', project_directory=f'{project_directory}\sanity-ecommerce-stripe')
            project_name = args.new_branch_name
            client_config_file = f'C:\\ProgramData\\Jenkins\\.jenkins\\workspace\\create_bussniss_config_file\\ecommerce\\jobs\\create_bussniss_config_file\\{project_name}_config.json'
            client_data_dict = load_json_to_dict(client_config_file)

            if client_data_dict:
                logger.info("JSON loaded successfully")
            else:
                logger.error("Failed to load JSON")
                return
            logger.info("Sanity satrt")

            if args.db_selected == "Sanity":
                sanity_vars = deploy_sanity(r"D:\ecommerce\react-ecommerce-website-stripe\sanity-ecommerce-stripe", project_name, args, client_data_dict)
                logger.info(sanity_vars)
            if args.db_selected == "Stripe":

                params = vars(args) | client_data_dict
                output = trigger_setup_strapi_job(params=params)


                # Regular expression pattern to extract the IP address
                match = re.search(r"STRAT_DROPLET_IP_ADDRESS_(\d+\.\d+\.\d+\.\d+)_END_DROPLET_IP_ADDRESS",
                                  output.console_output)

                # Check if a match is found and extract the IP
                if match :
                    public_ip_address = match.group(1)
                    print("Extracted IP Address:", public_ip_address)
                else:
                    print("No IP address found in the string.")

                match = re.search(r"API_TOKEN_START\s+(.+?)\s+API_TOKEN_END", output)

                if match:
                    api_token = match.group(1)
                    print("Extracted API Token:", api_token)
                else:
                    api_token = ""
                    print("API Token not found.")

                placeholders = {
                    '--PHONE_NUMBER_ID--': args.phone,
                    "--CLIENT_EMAIL--": client_data_dict.get('email'),
                    "--client_business_name_placeholder--": args.new_business_name,
                    "--CLIENT_PHONE--": client_data_dict.get('phone'),
                    "JWT_TOKEN_HOLDER": api_token
                }

                ecommerce_template_path = r"D:\ecommerce\react-ecommerce-website-stripe"
                vercel_json_path = r"D:\ecommerce\react-ecommerce-website-stripe\vercel_env.json"

                with open(vercel_json_path, 'w') as f:
                    json.dump(placeholders, f, indent=4)
                # if args.logo_file:
                #     destination_file = r"D:\ecommerce\react-ecommerce-website-stripe\public\maisamnakeuplogo.png"
                #     shutil.copy(args.logo_file, destination_file)
                replace_placeholders_in_repo(ecommerce_template_path, placeholders)
            project_git_manager.add_and_commit(commit_message=f"new push {datetime.now()} for user {args.new_business_name}", branch=f'feature/{args.new_branch_name}')
            project_git_manager.push(branch=f'feature/{args.new_branch_name}')
            deploy_vercel(project_name, branch= f'feature/{args.new_branch_name}')
    except Exception as e:
        handle_error(e, "here")



def main():
    try:
        args = get_job_params()
        subject = "Pipeline Started"
        body = f"Hello, \n\nThe pipeline has Started \n\nargs are:\n {args}.\n\nBest regards,\nYour Jenkins Pipeline"
        send_success_email(to_email=args.email, body=body, subject=subject)
        run_job()
        # add summary
        subject = "Pipeline Run Successful"
        body = f"Hello, \n\nThe pipeline has completed its run successfully.\n\nBest regards,\nYour Jenkins Pipeline"
        if args.email:
            send_success_email(to_email=args.email, body=body, subject=subject)
    except Exception as e:
        args = get_job_params()
        subject = "Pipeline Run Failed"
        body = f"Hello, \n\nThe pipeline has Failed its run with error {str(e)}.\n\nBest regards,\nYour Jenkins Pipeline"
        if args.email:
            send_success_email(to_email=args.email, body=body, subject=subject)
        handle_error(e)



def send_success_email(to_email, subject, body):
    # Set up the email details
    from_email = "khalildaibes1@gmail.com"  # Replace with your email


    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:

        YOUR_GOOGLE_EMAIL = 'khalildaibes1@gmail.com'  # The email you setup to send the email using app password
        YOUR_GOOGLE_EMAIL_APP_PASSWORD = 'rovx umao gokt fssy'  # The app password you generated

        smtpserver = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtpserver.ehlo()
        smtpserver.login(YOUR_GOOGLE_EMAIL, YOUR_GOOGLE_EMAIL_APP_PASSWORD)

        # Test send mail
        sent_from = YOUR_GOOGLE_EMAIL
        sent_to = to_email  #  Send it to self (as test)
        smtpserver.sendmail(sent_from, sent_to, body)

        # Close the connection
        smtpserver.close()
        logger.info(f"Success email sent to {to_email}")
    except Exception as e:
        logger.info(f"Failed to send email: {e}")

if __name__ == "__main__":

    main()




