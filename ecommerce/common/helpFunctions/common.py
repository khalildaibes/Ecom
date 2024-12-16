import json
import subprocess
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get the current working directory (workspace directory)
workspace_dir = os.getcwd()

def install_requirements():
    # Path to your requirements file
    requirements_file = f'{workspace_dir}\\requirements.txt'

    # Check if the requirements file exists
    if os.path.isfile(requirements_file):
        try:
            logger.info("Installing libraries from requirements.txt...")
            # Use subprocess to call pip and install libraries
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])
            logger.info("Libraries installed successfully.")
        except subprocess.CalledProcessError as e:
            logger.info(f"Error occurred while installing dependencies: {e}")
            sys.exit(1)
    else:
        logger.info(f"{requirements_file} not found.")
        sys.exit(1)
        
        
def load_json_to_dict(json_file_path):
    try:
        # Open the file at the given path and load it into a Python dictionary
        with open(json_file_path, 'r') as file:
            data_dict = json.load(file)
        return data_dict
    except FileNotFoundError:
        logger.info(f"Error: The file at {json_file_path} was not found.")
        return None
    except json.JSONDecodeError:
        logger.info(f"Error: Failed to decode JSON from the file at {json_file_path}.")
        return None
    except Exception as e:
        logger.info(f"An error occurred: {str(e)}")
        return None


def handle_error(e, fail_job=False, place="general"):
    logger.error(f"An error occurred at {place}: {str(e)}")
    if fail_job:
        logger.error("Stopping the job due to an error.")
        sys.exit(1)  # Exit immediately
    else:
        logger.info("Continuing the process despite the error.")