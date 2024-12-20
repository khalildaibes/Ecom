import argparse
import io
import json
import os
import re
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# from ecommerce.common.helpFunctions.common import install_requirements

from ecommerce.common.api.chatgpt import chatGptManager

def generate_config_json(
        email, password, new_business_name, small_description, template_id, categories,
        logo_file, phone, address, products_file=None, location_in_waze=None, css_file=None, banner_photo=None
    ):
    try:
        # Create a dictionary to hold the config data
        config_data = {
            "email": email,
            "password": password,
            "business": {
                "name": new_business_name,
                "description": small_description,
                "template_id": template_id,
                "categories": categories.split(',') if isinstance(categories, str) else categories,
                "logo_file": logo_file,
                "products_file": products_file,
                "phone": phone,
                "address": address,
                "location_in_waze": location_in_waze if location_in_waze else None,
                "css_file": css_file if css_file else None,
                "banner_photo": banner_photo if banner_photo else None
            }
        }

        # Define the output config JSON file name
        # Get the directory of the current script
        script_directory = os.path.dirname(os.path.abspath(__file__))

        # Define the output config JSON file path in the script's directory
        output_file = os.path.join(script_directory, f"{new_business_name}_config.json")
        
        # Write the dictionary to a JSON file
        with open(output_file, 'w', encoding='UTF-8') as json_file:
            json.dump(config_data, json_file, indent=4)

        print(f"Configuration file '{output_file}' generated successfully.")
    except Exception as e:
        # If URL-decoding fails, return the original text
          raise Exception("Sorry, failed to generate file") 

def update_translation_file(response_json):

    # Define the output config JSON file path in the script's directory
    translation_file = r"D:\ecommerce\react-ecommerce-website-stripe\translations\translations.js"

    # Read the content of the JS file
    with open(translation_file, 'r', encoding='utf-8') as file:
        js_content = file.read()

    # Update the translations in the JS file
    for lang, translations in response_json.items():
        for key, value in translations.items():
            # Build the regex to find the specific key-value pair
            pattern = rf"('{key}'\s*:\s*)'.*?'"
            
            replacement = rf"\1'{decode_garbled_text(value)}'"
            
            # Replace the old value with the new value in the js_content
            js_content = re.sub(pattern, replacement, js_content)

    # Write the updated content back to the file
    with open("output.js", 'w', encoding='utf-8') as file:
        file.write(js_content)
        
        
def decode_garbled_text(text):
    """
    Decodes URL-encoded or misencoded Unicode text.
    """
    try:
        # Try URL-decoding (for texts like Ø§Ù„Ø¹Ø±Ø¨ÙŠØ©)
        decoded_text = text.encode('windows-1252').decode('utf-8', errors='replace')
        print(decoded_text)
        return decoded_text

    except UnicodeEncodeError as e:
        print(f"UnicodeEncodeError: {e}")
    except UnicodeDecodeError as e:
        print(f"UnicodeDecodeError: {e}") 
    except Exception as e:
        # If URL-decoding fails, return the original text
        return text
    
def main():
    # install_requirements()
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

    args = parser.parse_args()

    # Call the function to generate the config JSON file
    generate_config_json(
        email=args.email,
        password=args.password,
        new_business_name=args.new_business_name,
        small_description=args.small_description,
        template_id=args.Template_ID,
        categories=args.categories,
        logo_file=args.logo_file,
        products_file=args.products_file,
        phone=args.phone,
        address=args.address,
        location_in_waze=args.location_in_waze,
        css_file=args.css_file,
        banner_photo=args.banner_photo
    )
    api_key = os.getenv('OPEN_AI_KEY')

    print(api_key)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    chatgpt_manager = chatGptManager.ChatGPTManager(api_key=os.getenv('OPEN_AI_KEY'))
    response_json = chatgpt_manager.generate_json_data(project_name=args.new_business_name)
    
    # Get the directory of the current script
    update_translation_file(response_json)

if __name__ == "__main__":
    main()
