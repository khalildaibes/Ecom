import json




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