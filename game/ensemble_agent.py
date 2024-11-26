import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
from llama_agent import Llama3_Agent
from llama2_agent import Llama2_Agent
from phi3_agent import Phi3_Agent
from qwen_agent import Qwen_Agent
from gemma_agent import GEMMA_Agent
from util import naive_json_from_text
from collections import defaultdict

#may need to set ollama params
#OLLAMA_NUM_PARALLEL=4 OLLAMA_MAX_LOADED_MODELS=4 ./ollama serve

#commands to preload models
#curl http://localhost:11434/api/generate -d '{ "model": "llama3.1:8b-instruct-q5_K_M" }'
#curl http://localhost:11434/api/generate -d '{ "model": "phi3:medium-128k" }'
#curl http://localhost:11434/api/generate -d '{ "model": "qwen2.5:7b" }'
class Ensemble_Agent():
    def __init__(self):
        self.name = "ensemble"
        # self.llms=["llama3", "phi3", "qwen"]
        self.agents=[]
        self.agents.append(Llama3_Agent())
        self.agents.append(Phi3_Agent())
        self.agents.append(Qwen_Agent())
        # self.agents.append(GEMMA_Agent())
        self.selection_count = defaultdict(int)

    def query(self, prompt):
        def get_response(agent):
            res = naive_json_from_text(agent.query(prompt))
            max_attempts = 2
            while res is None:
                if max_attempts <= 0:
                    return None
                res = naive_json_from_text(agent.query(prompt))
                max_attempts -= 1
            return res, agent.name
        responses=[]

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(get_response, agent) for agent in self.agents]
            for future in as_completed(futures, timeout=1000):
                try:
                    result = future.result()
                    if result is not None:
                        responses.append(future.result())
                except Exception as e:
                    print(f"Error in agent response: {e}")
        if not responses:
            return "" # this should trigger the invalid JSON catch in game.py to reattempt the action and log the failure
        print(responses)
        selections = [response['selection'] for response, name in responses]
        selection_counts = Counter(selections)
        most_common_selection, _ = selection_counts.most_common(1)[0]
        for response, name in responses:
            if response['selection'] == most_common_selection:
                self.selection_count[name] += 1
        print("ensemble counts", dict(self.selection_count))
        
        # reasons = [response['reasons'] for response in responses if response['selection'] == most_common_selection]

        return json.dumps({"selection": most_common_selection})
