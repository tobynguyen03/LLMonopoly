import os
import requests
import json
from mistralai import Mistral


class MistralAgent:
    
    def __init__(self, model="mistral:latest"):
        self.url = "http://localhost:11434/api/generate"
        self.api_key= os.environ.get("MISTRAL_API_KEY", "aa4xOzZ262TSBj0WxVmJ3KjQQqSD8eFE")
        self.model = "mistral:latest"
        self.client = Mistral(api_key=self.api_key)

    def query(self, prompt):
        data = {
            "model": self.model,
            # "messages": [
                # {
                #     "role": "user",
            "content": prompt,
                #     "temperature": 0.7,
                #     "max_tokens": 150
                # }
            # ],
            "stream": False
        }

        # HTTP headers
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'

        }

        # Make the POST request
        try:
            response = requests.post(self.url, headers=headers, json=data)
            # print(f"Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")
            # Check if the request was successful
            if response.status_code == 200:
                res_json = response.json()
                if 'response' in res_json and res_json['response']:
                    return res_json['response']
                else:
                    print(f"Empty response. Reason: {res_json.get('done_reason', 'unknown')}")
                    return ''
            #     return res_json['message']['content']  # Extract the message content
            else:
                print(f"Error: {response.status_code}, {response.text}")
                return ''
        except Exception as e:
            print(f"Error querying Mistral: {e}")
            return ''

        
if __name__ == "__main__":
    agent = MistralAgent()
    prompt = "Hello, world!"
    response = agent.query(prompt)
    print("Response from MistralAgent:", response)

