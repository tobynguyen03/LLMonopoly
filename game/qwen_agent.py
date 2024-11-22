import requests
import json
class Qwen_Agent():
    def __init__(self):
        # Uses LLama3.2 via ollama, need to have ollama running for API to work
        self.url = "http://localhost:11434/api/generate"
    def query(self, prompt):
        data = {
            "model": "qwen2.5:7b",
            "prompt": prompt,
            # "messages": [
            #     {
            #     "role": "user",
            #     "content": prompt
            #     }
            # ],
            "stream": False
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(self.url, headers=headers, json=data)
        # return (response.json())
        return (response.json()['response'])