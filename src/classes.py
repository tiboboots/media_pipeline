import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()

class APICall:
    def __init__(self, endpoint, parameters):
        self.api_key = os.getenv("tmdb_api_key")
        self.file_path = "response.json"
        self.endpoint = endpoint
        self.parameters = parameters.copy()
        self.parameters['api_key'] = self.api_key
        self.api_url = f"https://api.themoviedb.org/3/{endpoint}"
    def make_request(self):
        try:
            response = requests.get(url = self.api_url, params = self.parameters)
            json_response = response.json()
            return json_response
        except requests.exceptions.HTTPError as e:
            print(f"Status code error: {response.status_code}")
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {e}")
        except requests.exceptions.Timeout as t:
            print(f"Request timeout: {t}")
    def save_response(self, json_response):
        with open(self.file_path, "w") as json_file:
            json.dump(json_response, json_file, indent = 4)
            print("Successfully saved response to json file.")