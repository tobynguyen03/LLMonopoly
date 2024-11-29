import os
import requests
import json
from mistralai import Mistral
class MistralAgent:
    def __init__(self, model="mistral:latest"):
        self.url = "http://localhost:11434/api/chat"

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
    
if __name__ == "__main__":
    agent = MistralAgent()
    prompt = "WHat is the most sold phone?"
    response = agent.query(prompt)
    print("Response from MistralAgent:", response)
   