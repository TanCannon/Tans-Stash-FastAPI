import os, json
'''we can use the json file here to add our own parameters'''
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(BASE_DIR, "config.json")

# print(f"CONFIG_PATH:{config_path}")

with open(config_path,'r') as c: #reading from json file the urls
    params = json.load(c)['params']