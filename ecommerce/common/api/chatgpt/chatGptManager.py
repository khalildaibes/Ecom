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
        
    def remove_before_first_brace(self, text):
        # Find the index of the first '{'
        first_brace_index = text.find('{')
        
        # If '{' is found, return the substring starting from that index
        if first_brace_index != -1:
            return text[first_brace_index:]
        else:
            return text  # If no '{' is found, return the original text

    def extract_before_last_brace(self, text):
        # Find the index of the last '}'
        last_brace_index = text.rfind('}')
        
        # If '}' is found, return the substring before it
        if last_brace_index != -1:
            return text[:last_brace_index+1]  # Include the last brace
        else:
            return text  # If no '}' is found, return the original text

    def fix_json_format(self, json_string):
        # Replace single quotes with double quotes
        json_string = json_string.replace("'", '"')

        # Add double quotes around the unquoted keys like en, ar, he
        json_string = re.sub(r'(\w+):', r'"\1":', json_string)

        return json_string

    def transform_generated_translations_to_dict(self,translations_text):
        """
        Transforms the JavaScript-style translations text into a Python dictionary.
        Removes the 'const translations =' part and converts the remaining valid JSON to a Python dictionary.
        """
        # Step 1: Remove the 'const translations =' part
        # Using regex to remove everything before the opening curly brace
        print(translations_text)
        clean_text = self.remove_before_first_brace(translations_text)
        clean_text = self.extract_before_last_brace(clean_text)
        clean_text = self.fix_json_format(clean_text)
        # Step 2: Ensure the remaining string is valid JSON
        # Replace single quotes with double quotes to make it valid JSON

        # Step 3: Parse the JSON text into a Python dictionary
        try:
            print(clean_text)
            translations_dict = json.loads(clean_text)
            print("converted")
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
                        "dont write anything beside the generated json value withour declaring anything else, make sure the reposnse is in utf-8"+
                        """ like this  {
                                    "en": {
                                        'brands': 'Brands',
                                        'aboutUsDescription': 'Khalil Bakery is dedicated to providing the finest baked goods made from the freshest ingredients. Our passion for baking ensures that each product is crafted with care and love.',
                                        'testimonial1': 'The pastries from Khalil Bakery are simply the best! I can’t get enough of them.',
                                        'testimonial2': 'A delightful experience every time I visit. The bread is always fresh and delicious!',
                                        'testimonialName1': 'Yael',
                                        'testimonialName2': 'Oren'
                                    },
                                    "ar": {
                                        'brands': 'شركات',
                                        'aboutUsDescription': 'مخبز خليل مكرس لتقديم أفضل المخبوزات المصنوعة من المكونات الطازجة. شغفنا بالخبز يضمن أن يتم صنع كل منتج بعناية وحب.',
                                        'testimonial1': 'المعجنات من مخبز خليل هي الأفضل! لا أستطيع الحصول على ما يكفي منها.',
                                        'testimonial2': 'تجربة رائعة في كل مرة أزور فيها. الخبز دائمًا طازج ولذيذ!',
                                        'testimonialName1': 'أحمد',
                                        'testimonialName2': 'سارة'
                                    },
                                    "he": {
                                        'brands': 'חברות',
                                        'aboutUsDescription': 'מאפיית חאליל מחויבת לספק את מוצרי המאפים המשובחים ביותר העשויים מהמרכיבים הטריים ביותר. התשוקה שלנו לאפייה מבטיחה שכל מוצר נעשה בקפידה ובאהבה.',
                                        'testimonial1': 'המאפים ממאפיית חאליל הם פשוט הטובים ביותר! אני לא יכול להפסיק לאכול אותם.',
                                        'testimonial2': 'חוויה מדהימה בכל פעם שאני מבקר. הלחם תמיד טרי וטעים!',
                                        'testimonialName1': 'יעל',
                                        'testimonialName2': 'אורן'
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

                return self.transform_generated_translations_to_dict(translations_text=res)

            except Exception as e:
                res = response_json['choices'][0]['message']['content']
                print(str(e))
                print(f"response_json   {res}")
                return {"error": f"Failed to process response: {str(e)}"}
        print(f"Error im response_json   {response_json}")
        raise Exception("Sorry, Failed getting AI response") 

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

