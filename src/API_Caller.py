import os
import requests
import json

from Local_data.api_key import *

'''
This Application uses the edamam API, allowing for recipe searching.



'''

base_url = "https://api.edamam.com/search"
header = "Accept-Encoding: gzip"


