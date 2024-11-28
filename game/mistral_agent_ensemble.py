import requests
import json

# agent used for ensemble trials
class Mistral_Agent():
    def __init__(self):
        # Uses LLama3 via ollama, need to have ollama running for API to work
        self.url = "http://localhost:11434/api/generate"
        self.name = "Mistral"

    def query(self, prompt):
        data = {
            "model": "mistral:7b-instruct",
            # "temperature": 0.3,
            "prompt": prompt,
            "stream": False
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(self.url, headers=headers, json=data)
        return(response.json()['response'])
