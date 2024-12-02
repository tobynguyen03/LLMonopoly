import os
import requests
import json

class Mistral_Agent:
    def __init__(self):
        self.url = "http://localhost:11434/api/chat"
        self.name = "Mistral"

    def query(self, prompt):
        data = {
            "model": "mistral:latest",
            "messages": [
                {
                "role": "user",
                "content": prompt
                }
            ],
            "stream": False
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(self.url, headers=headers, json=data)
        # return (response.json())
        return(response.json()['message']['content'])