import requests
from dotenv import load_dotenv
import os

load_dotenv()

class APICall:
    def __init__(self, endpoint, parameters):
        self.api_key = os.getenv("tmdb_api_key")
        self.endpoint = endpoint
        self.parameters = parameters.copy()
        self.parameters['api_key'] = self.api_key
        self.api_url = f"https://api.themoviedb.org/3/{endpoint}"
    def make_request(self):
        response = requests.get(url = self.api_url, params = self.parameters)
        if response.status_code == 200:
            valid_response = response.json()
            return valid_response
        else:
            print(f"Error. Status code: {response.status_code}")
            return
        
        


        



