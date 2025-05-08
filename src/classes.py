import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()

class APICall:
    def __init__(self, endpoint, version, params, headers, data = None):
        self.access_token = os.getenv("tmdb_access_token")
        self.data = data
        self.file_path = "response.json"
        self.endpoint = endpoint
        self.version = version
        self.parameters = params.copy()
        self.headers = headers.copy()
        self.headers['Authorization'] = f"Bearer {self.access_token}"
        self.api_url = f"https://api.themoviedb.org/{version}/{endpoint}"
    def make_request(self):
        try:
            response = requests.get(url = self.api_url, params = self.parameters, headers = self.headers)
            json_response = response.json()
            return json_response
        except requests.exceptions.HTTPError:
            print(f"Status code error: {response.status_code}")
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {e}")
        except requests.exceptions.Timeout as t:
            print(f"Request timeout: {t}")
    def save_response(self, json_response):
        with open(self.file_path, "w") as json_file:
            json.dump(json_response, json_file, indent = 4)
            print("Successfully saved response to json file.")
    def send_data(self):
        try:
            response = requests.post(self.api_url, headers = self.headers, json = self.data)
            json_response = response.json()
            return json_response
        except requests.exceptions.HTTPError:
            print(f"Status code error: {response.status_code}")
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {e}")
        except requests.exceptions.Timeout as t:
            print(f"Request timeout: {t}")
