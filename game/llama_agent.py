import requests
import json
class Llama3_Agent():
    def __init__(self):
        self.url = "http://localhost:11434/api/chat"
    def query(self, prompt):
        data = {
            "model": "llama3.2",
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