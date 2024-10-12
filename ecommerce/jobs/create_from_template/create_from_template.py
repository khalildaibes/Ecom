import argparse
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from ecommerce.common.api.jenkinsAPI.jenkinsManager import JenkinsJob, JenkinsManager
from ecommerce.common.api.github.gitManager import GitManager
from ecommerce.common.api.sanity.saintyManager import SanityManager
from ecommerce.common.api.vercel.vercelManager import VercelManager
from ecommerce.common.helpFunctions.common import load_json_to_dict


def trigger_create_config_file_job(params):
    jenkins_manager = JenkinsManager(jenkins_url="http://localhost:8080", username="kdaibes", api_token="Kh6922er!")
    return jenkins_manager.trigger_and_wait_for_output("create_bussniss_config_file", params)


def get_job_params():
    parser = argparse.ArgumentParser(description="Generate a config JSON file from parameters")
    required_args = ['email', 'password', 'new_business_name', 'small_description', 'Template_ID', 'categories', 'logo_file', 'phone', 'address']
    for arg in required_args:
        parser.add_argument(f'--{arg}', required=True)

    parser.add_argument('--products_file', '--location_in_waze', '--css_file', '--banner_photo', required=False)
    return parser.parse_args()


def replace_placeholders_in_repo(repo_path, placeholders):
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(('.txt', '.py', '.html', '.js', '.json', '.md', '.env')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()

                    updated_content = content
                    for placeholder, replacement in placeholders.items():
                        if replacement:
                            updated_content = updated_content.replace(placeholder, replacement)

                    if updated_content != content:
                        with open(file_path, 'w') as f:
                            f.write(updated_content)
                        print(f"Replaced placeholders in {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")


def setup_git_manager(project_directory, github_username):
    return GitManager(project_directory, github_username, os.getenv("GITHUB_TOKEN"))


def deploy_sanity(sanity_project_dir, project_name):
    sanity_token = os.getenv("SANITY_ADMIN_TOKEN")
    manager = SanityManager(sanity_project_dir, sanity_token)
    manager.sanity_init()
    # TODO fix sanity studi o creation
    # manager.create_sanity_studio(project_name)
    manager.sanity_deploy()
    return manager.get_sanity_variables()


def deploy_vercel(project_directory, project_name):
    manager = VercelManager(
        project_name=project_name,
        github_username="khalildaibes",
        github_token=os.getenv("GITHUB_TOKEN"),
        vercel_token=os.getenv("VercelToken")
    )
    manager.init_vercel_project()
    manager.link_vercel_project()
    manager.deploy_vercel()


def run_job():
    args = get_job_params()
    config_create_job = trigger_create_config_file_job(vars(args))
    config_create_job = True
    if config_create_job:
        project_name = args.new_business_name
        script_file_dir= os.getenv("WORKSPACE")
        workspace= os.path.dirname(script_file_dir)
        client_config_file = f'{workspace}\\create_bussniss_config_file\ecommerce\jobs\create_bussniss_config_file\\{project_name}_config.json'
        print(f"workspace is {client_config_file}")
        client_data_dict = load_json_to_dict(client_config_file)
        ecommerce_template_path = r"D:\ecommerce\react-ecommerce-website-stripe"
        if client_data_dict:
            print("JSON loaded successfully:", client_data_dict)
        else:
            print("Failed to load JSON.")
            return

        placeholders = {
            "#CLIENT_EMAIL#": client_data_dict.get('email'),
            "#CLIENT_BUSINESS_NAME#": project_name,
            "#CLIENT_PHONE#": client_data_dict.get('phone'),
            # TODO: "add other needed placeholders like sanity api and sanity project vercel ect..."
        }

        sanity_vars = deploy_sanity(r"D:\ecommerce\react-ecommerce-website-stripe\sanity-ecommerce-stripe", project_name)
        print(sanity_vars)

        replace_placeholders_in_repo(ecommerce_template_path, placeholders)

        deploy_vercel(ecommerce_template_path, project_name)

def main():
    
    try:
        run_job()

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        decision = 'yes'
        if decision == 'yes' :
            sys.exit(1)  # Exit immediately after stopping the job
        else:
            print("Continuing the process With ERRORS  ...")


if __name__ == "__main__":
    main()
