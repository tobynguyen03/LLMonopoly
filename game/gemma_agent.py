import requests
import json

class GEMMA_Agent():
    def __init__(self):
        self.url = "http://localhost:11434/api/chat"
        self.model = "gemma2:9b"

    def query(self, prompt):
        data = {
            "model": self.model,
            "prompt": prompt,
            "temperature": 0.7,
            "max_tokens": 150,
            "stop": ["<start_of_turn>", "<end_of_turn>"]
        }

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(self.url, headers=headers, json=data)
        if response.status_code == 200:
            res_json = response.json()
            return res_json['choices'][0]['text']
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return ''

if __name__ == "__main__":
    agent = GEMMA_Agent()
    prompt = "Hello, how are you?"
    response = agent.query(prompt)
    print("Response from GEMMA_Agent:", response)
