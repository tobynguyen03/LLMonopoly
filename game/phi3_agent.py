import requests
import json

class Phi3_Agent():
    def __init__(self):
        self.url = "http://localhost:11434/api/chat"
        self.name = "Phi-3"
        
    def query(self, prompt):
        data = {
            "model": "phi3:medium",
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
        return response.json().get('message', {}).get('content', '')