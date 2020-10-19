import os
import requests
import json

from Local_data.api_key import *

'''
This Application uses the edamam API, allowing for recipe searching.



'''


class EdamamAPI:
    def __init__(self, base_url, header):
        self.base_url = base_url
        self.header = header

    def ingredient_query(self, query):
        target_url = f"{self.base_url}?q={query}&app_id={application_ID}&app_key={application_keys}"
        response = requests.get(target_url, headers=self.header)
        json_data = response.json()
        print(json.dumps(json_data, indent=2))


api_caller = EdamamAPI("https://api.edamam.com/search", {"Accept-Encoding": "gzip"})

api_caller.ingredient_query(input("Choose and ingredient: \n"))
