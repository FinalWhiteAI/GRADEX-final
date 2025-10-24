import json
import os

DATA_DIR = "./data"

def load_json(file):
    path = os.path.join(DATA_DIR, file)
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump([], f)
    with open(path, "r") as f:
        return json.load(f)

def save_json(file, data):
    path = os.path.join(DATA_DIR, file)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
