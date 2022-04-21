import requests
import json
from pprint import pprint

def get_repo(url: str) -> list:
    response = requests.get(url).json()
    repo = []
    for el in response:
        repo.append(el['name'])
    return repo

username = (input("Enter username "))
url_1 = 'https://api.github.com/users/'+username+'/repos'

repos = get_repo(url_1)

with open('repos.json', 'w') as f:
    json_repo = json.dump(repos, f)
