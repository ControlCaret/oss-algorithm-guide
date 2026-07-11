import json
import os
from functools import lru_cache

@lru_cache(maxsize=1)
def load_problems(file_path=None):
    if file_path is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "data", "leetcode_problems.json")
    
    if not os.path.exists(file_path):
        return []
        
    with open(file_path, mode="r", encoding="utf-8") as f:
        return json.load(f)
