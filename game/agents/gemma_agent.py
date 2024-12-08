import requests
import json

class GEMMA_Agent():
    def __init__(self):
        self.url = "http://localhost:11434/api/chat"
        self.name = "Gemma"

    def query(self, prompt):
        data = {
            "model": "gemma2:9b",
            "prompt": prompt,
            "temperature": 0.7,
            "max_tokens": 150,
            "stop": ["<start_of_turn>", "<end_of_turn>"]
        }

        headers = {
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(self.url, headers=headers, json=data)

            if response.status_code == 200:
                res_json = response.json()

                if 'message' in res_json and 'content' in res_json['message']:
                    return res_json['message']['content']
                else:
                    print("Error: Unexpected response format")
                    print("Response JSON:", res_json)
                    return ''
            else:
                print(f"Error: {response.status_code}, {response.text}")
                return ''
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return ''

if __name__ == "__main__":
    agent = GEMMA_Agent()
    prompt = "Hello, how are you?"
    response = agent.query(prompt)
    print("Response from GEMMA_Agent:", response)
