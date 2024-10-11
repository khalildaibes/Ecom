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
                        "text": "We are a company that builds eCommerce websites. Generate JSON translations in this format: " +
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
                # Extract the JSON-like structure from the response
                print(f"response is {res}")
                response_content = response_json["choices"][0]["message"]["content"]

                # In this case, we expect the model to respond with a string we can directly treat as a Python dict
                # First, try to parse the response as JSON
                json_data = response_content.strip()
                
                # Check if the response can be loaded directly as a dictionary
                try:
                    parsed_data = eval(json_data)  # Using eval to evaluate the string as Python code
                    return parsed_data
                except SyntaxError as e:
                    print(str(e))
                    return {"error": f"Failed to parse response as JSON: {str(e)}"}

            except Exception as e:
                print(str(e))
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



