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

#may need to set ollama params
#OLLAMA_NUM_PARALLEL=4 OLLAMA_MAX_LOADED_MODELS=4 ./ollama serve

class Ensemble_Agent():
    def __init__(self):
        self.name = "ensemble"
        # self.llms=["llama3", "phi3", "qwen"]
        self.agents=[]
        self.agents.append(Llama3_Agent())
        self.agents.append(Phi3_Agent())
        self.agents.append(Qwen_Agent())
        # self.agents.append(GEMMA_Agent())

    def query(self, prompt):
        def get_response(agent):
            res = naive_json_from_text(agent.query(prompt))
            while res is None:
                res = naive_json_from_text(agent.query(prompt))
            return res
        responses=[]

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(get_response, agent) for agent in self.agents]
            for future in as_completed(futures, timeout=20):
                try:
                    responses.append(future.result())
                except Exception as e:
                    print(f"Error in agent response: {e}")
        if not responses:
            raise RuntimeError("No responses collected from agents.")

        print(responses)
        selections = [response['selection'] for response in responses]
        selection_counts = Counter(selections)
        most_common_selection, _ = selection_counts.most_common(1)[0]

        # reasons = [response['reasons'] for response in responses if response['selection'] == most_common_selection]

        return json.dumps({"selection": most_common_selection})
