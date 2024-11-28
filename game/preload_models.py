import concurrent.futures
import requests
import time

#update model names accordingly
models = [
    "llama3.1:8b-instruct-q5_K_M",
    "phi3:medium-128k",
    "qwen2.5:7b",
    "gemma2:9b",
    "mistral:7b-instruct",
]

url = "http://localhost:11434/api/generate"

def load_model(model):
    payload = {"model": model, "keep_alive": -1}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return f"Successfully loaded {model}"
        else:
            return f"Failed to load {model}: {response.status_code}, {response.text}"
    except Exception as e:
        return f"Error loading {model}: {e}"

if __name__ == "__main__":
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(load_model, model) for model in models]
        for future in concurrent.futures.as_completed(futures):
            print(future.result())
    end_time = time.time()
    print(f"Models loaded in: {end_time - start_time:.2f} seconds")
