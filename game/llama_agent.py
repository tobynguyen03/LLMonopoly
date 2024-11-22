import requests
import json

class Llama3_Agent():
    def __init__(self):
        # Uses LLama3.2 via ollama, need to have ollama running for API to work
        self.url = "http://localhost:11434/api/generate"

    def query(self, prompt):
        data = {
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(self.url, headers=headers, json=data)
        return(response.json()['response'])
