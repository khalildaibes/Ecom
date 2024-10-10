import json
import subprocess
import sys
import os

# Get the current working directory (workspace directory)
workspace_dir = os.getcwd()

def install_requirements():
    print(f"heeere {workspace_dir} heere ")
    # Path to your requirements file
    requirements_file = workspace_dir.join(r'requirements.txt')

    # Check if the requirements file exists
    if os.path.isfile(requirements_file):
        try:
            print("Installing libraries from requirements.txt...")
            # Use subprocess to call pip and install libraries
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])
            print("Libraries installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while installing dependencies: {e}")
            sys.exit(1)
    else:
        print(f"{requirements_file} not found.")
        sys.exit(1)
        
        
def load_json_to_dict(json_file_path):
    try:
        # Open the file at the given path and load it into a Python dictionary
        with open(json_file_path, 'r') as file:
            data_dict = json.load(file)
        return data_dict
    except FileNotFoundError:
        print(f"Error: The file at {json_file_path} was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from the file at {json_file_path}.")
        return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None