import json
from pathlib import Path

BASE_PATH = Path.cwd().joinpath('tests', 'data')

def read_json_file(fname):
    """
    Reads a json file and returns the data as a dictionary
    """
    
    if not fname.endswith('.json'): fname += '.json'
    
    with open(BASE_PATH.joinpath(fname)) as json_file:
        return json.load(json_file)