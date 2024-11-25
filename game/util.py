import json
import re

def naive_json_from_text(text):
    match = re.search(r'\{[\s\S]*\}', text)
    # catching cases where llm adds an explanation after the json
    if not match:
        return None

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        print(f"Invalid JSON: {e}")
        return None