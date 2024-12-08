import requests
import json

class Llama2_Agent():
    def __init__(self):
        # Uses LLama2 via ollama, need to have ollama running for API to work
        self.url = "http://localhost:11434/api/chat"
        self.name = "Llama-2"

    def query(self, prompt):
        data = {
            "model": "llama2",
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