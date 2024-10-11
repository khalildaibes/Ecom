import requests
import re
import json
from dotenv import load_dotenv
import os


class ChatGPTManager:
    def __init__(self, api_key):
        """
        Initialize the ChatGPTManager with an API key.
        """
        self.api_key =api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }


    def transform_generated_translations_to_dict(self,translations_text):
        """
        Transforms the JavaScript-style translations text into a Python dictionary.
        Removes the 'const translations =' part and converts the remaining valid JSON to a Python dictionary.
        """
        # Step 1: Remove the 'const translations =' part
        # Using regex to remove everything before the opening curly brace
        clean_text = re.sub(r"const translations\s*=\s*", "", translations_text.strip(), 1)
        
        # Step 2: Ensure the remaining string is valid JSON
        # Replace single quotes with double quotes to make it valid JSON
        clean_text = clean_text.replace("'", '"')
        clean_text = clean_text.replace("`", '')
        print(f"clean_text {clean_text}")
        
        # Step 3: Parse the JSON text into a Python dictionary
        try:
            translations_dict = json.loads(clean_text)
            return translations_dict
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            return None
        
    def send_request(self, payload):
        """
        Send a request to the OpenAI API with the given payload.
        :param payload: The payload to send to the OpenAI API.
        :return: The JSON response from the API or error message.
        """
        try:
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=self.headers, json=payload)
            response.encoding = 'utf-8'
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Error occurred: {response.status_code}, {response.text}"}
        except Exception as e:
            return {"error": f"Exception occurred: {str(e)}"}

    def generate_json_data(self, project_name):
        """
        Generate JSON data for translations in multiple languages (English, Arabic, Hebrew).
        :return: Generated JSON data from the GPT model in the required format.
        """
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "We are a company that builds eCommerce websites. make sure your reponse content dosnt include anything else besides the json "+
                        "dont write anything beside the generated json value withour declaring anything else "+
                        """ like this  {
  en: {
    'brands': 'Brands',
    'aboutUsDescription': 'Khalil Bakery is dedicated to providing the finest baked goods made from the freshest ingredients. Our passion for baking ensures that each product is crafted with care and love.',
    'testimonial1': 'The pastries from Khalil Bakery are simply the best! I canג€™t get enough of them.',
    'testimonial2': 'A delightful experience every time I visit. The bread is always fresh and delicious!',
    'testimonialName1': 'Yael',
    'testimonialName2': 'Oren'
  },
  ar: {
    'brands': '״´״±�ƒ״§״×',
    'aboutUsDescription': '�…״®״¨״² ״®�„���„ �…�ƒ״±״³ �„״×�ˆ����״± ״£��״¶�„ ״§�„�…״®״¨�ˆ״²״§״× ״§�„�…״µ�†�ˆ״¹״© �…�† ״£״¬�ˆ״¯ ״§�„�…�ƒ�ˆ�†״§״×. ״´״÷���†״§ ״¨״§�„״®״¨״² ��״¶�…�† ״£�† �ƒ�„ �…�†״×״¬ ��״×�… ״×״µ�†��״¹�‡ ״¨״¹�†״§��״© �ˆ״­״¨.',
    'testimonial1': '״§�„�…״¹״¬�†״§״× �…�† �…״®״¨״² ״®�„���„ �‡�� ״¨״¨״³״§״·״© ״§�„״£��״¶�„! �„״§ ״£״³״×״·��״¹ ״§�„״­״µ�ˆ�„ ״¹�„�‰ �…״§ ���ƒ���� �…�†�‡״§.',
    'testimonial2': '״×״¬״±״¨״© ״±״§״¦״¹״© ���� �ƒ�„ �…״±״© ״£״²�ˆ״± �����‡״§. ״§�„״®״¨״² ״¯״§״¦�…״§�‹ ״·״§״²״¬ �ˆ�„״°��״°!',
    'testimonialName1': '��״§�„',
    'testimonialName2': '״£�ˆ״±�†'
  },
  he: {
    'brands': '׳—׳‘׳¨׳•׳×',
    'aboutUsDescription': '׳�׳�׳₪׳™׳™׳× ׳—׳�׳™׳� ׳�׳—׳•׳™׳‘׳× ׳�׳¡׳₪׳§ ׳�׳× ׳”׳�׳�׳₪׳™׳� ׳”׳˜׳•׳‘׳™׳� ׳‘׳™׳•׳×׳¨ ׳”׳¢׳©׳•׳™׳™׳� ׳�׳”׳�׳¨׳›׳™׳‘׳™׳� ׳”׳˜׳¨׳™׳™׳� ׳‘׳™׳•׳×׳¨. ׳”׳×׳©׳•׳§׳” ׳©׳�׳ ׳• ׳�׳�׳₪׳™׳™׳” ׳�׳‘׳˜׳™׳—׳” ׳©׳›׳� ׳�׳•׳¦׳¨ ׳�׳™׳•׳¦׳¨ ׳‘׳�׳”׳‘׳” ׳•׳‘׳“׳�׳’׳”.',
    'testimonial1': '׳”׳�׳�׳₪׳™׳� ׳�׳�׳�׳₪׳™׳™׳× ׳—׳�׳™׳� ׳₪׳©׳•׳˜ ׳”׳˜׳•׳‘׳™׳� ׳‘׳™׳•׳×׳¨! ׳�׳ ׳™ ׳�׳� ׳™׳›׳•׳� ׳�׳”׳₪׳¡׳™׳§ ׳�׳�׳›׳•׳� ׳�׳•׳×׳�.',
    'testimonial2': '׳—׳•׳•׳™׳” ׳ ׳¢׳™׳�׳” ׳‘׳›׳� ׳₪׳¢׳� ׳©׳�׳ ׳™ ׳�׳‘׳§׳¨. ׳”׳�׳—׳� ׳×׳�׳™׳“ ׳˜׳¨׳™ ׳•׳˜׳¢׳™׳�!',
    'testimonialName1': '׳™ײ°׳¢ײµ׳�',
    'testimonialName2': '׳�׳•ײ¹׳¨ײ¶׳�'
  }
}"""+ 
                        ".  Generate JSON translations in this format: " +
                                "const translations = { en: { 'brands': 'Brands', ... }, ar: { 'brands': 'شركات', ... }, he: { 'brands': 'חברות', ... } }. " +
                                f"Include generated text and translations for a website that is named {project_name}, aboutUsDescription, testimonial1, testimonial2, testimonialName1, testimonialName2."+
                                "testimonial1 is what the client said about us as a review and the testimonialName1 is the name of the client choose mostly hebrew names for a girl and a boy"
                    }
                ]
            }
        ]

        payload = {
            "model": "gpt-4o-mini",
            "messages": messages,
            "max_tokens": 1000
        }
        response_json = self.send_request(payload)
        if "error" not in response_json:
            try:
                res = response_json['choices'][0]['message']['content']
                response_dict = self.transform_generated_translations_to_dict(translations_text=res)

                # Extract the JSON-like structure from the response
                print(f"response is {res}")
                response_content =res

                # In this case, we expect the model to respond with a string we can directly treat as a Python dict
                # First, try to parse the response as JSON
                json_data = response_content.strip()
                
                # Check if the response can be loaded directly as a dictionary
                try:
                    parsed_data = eval(json_data)  # Using eval to evaluate the string as Python code
                    return response_dict
                except SyntaxError as e:
                    print(str(e))
                    res = response_json['choices'][0]['message']['content']
                    print(f"response_json   {res}")
                    return {"error": f"Failed to parse response as JSON: {str(e)}"}

            except Exception as e:
                res = response_json['choices'][0]['message']['content']
                print(str(e))
                print(f"response_json   {res}")
                return {"error": f"Failed to process response: {str(e)}"}
        
        return response_json

    def generate_data_from_text(self, user_input_text):
        """
        General function to send any text-based request to GPT model.
        :param user_input_text: The user input text.
        :return: The GPT model's response.
        """
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_input_text
                    }
                ]
            }
        ]

        payload = {
            "model": "gpt-4o-mini",
            "messages": messages,
            "max_tokens": 1000
        }

        return self.send_request(payload)



