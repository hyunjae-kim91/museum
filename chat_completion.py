import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import openai
import requests

load_dotenv()

class chatCompletion:

    def __init__(self) -> None:
        self.OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

    def get_answer(self, query):
        OPENAI_API_KEY = self.OPENAI_API_KEY
        url = "https://api.openai.com/v1/chat/completions"
        model = "gpt-4o-mini"
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": query
                }
            ],
            "temperature": 0.4
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }

        response = requests.request("POST", url, json=payload, headers=headers)

        return response.text

    def get_validation(self, query):
        OPENAI_API_KEY = self.OPENAI_API_KEY
        url = "https://api.openai.com/v1/chat/completions"
        model = "gpt-4o"
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": query
                }
            ],
            "temperature": 0.1
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }

        response = requests.request("POST", url, json=payload, headers=headers)

        return response.text