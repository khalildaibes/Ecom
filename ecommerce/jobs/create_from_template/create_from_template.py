import argparse
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from ecommerce.common.api.jenkinsAPI.jenkinsManager import JenkinsManager
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
            if file.endswith(('.txt', '.py', '.html', '.js', '.json', '.md')):
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
    manager.change_to_project_dir()
    manager.sanity_init()
    manager.create_sanity_studio(project_name)
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


def main():
    args = get_job_params()
    config_create_job = trigger_create_config_file_job(vars(args))

    if config_create_job:
        project_name = args.new_business_name
        project_directory = r"D:\ecommerce\react-ecommerce-website-stripe"
        client_config_file = os.path.join(project_directory, "ecommerce", "jobs","create_bussniss_config_file", f"{project_name}_config.json")
        client_data_dict = load_json_to_dict(client_config_file)

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

        replace_placeholders_in_repo(project_directory, placeholders)

        deploy_vercel(project_directory, project_name)


if __name__ == "__main__":
    main()
