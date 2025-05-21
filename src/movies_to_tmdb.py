import csv
import time
import json
import yaml
from api_call_class import APICall

class TMDBCredentials:
    read_access_token = None
    write_access_token = None
    account_id = None

    @classmethod
    def get_secrets_config(cls):
        with open("secrets.yaml", "r") as config_yml:
            config_secrets = yaml.safe_load(config_yml)
        cls.read_access_token = config_secrets['tmdb_read_access_token']
        cls.write_access_token = config_secrets['tmdb_write_access_token']
        return config_secrets

    @classmethod
    def get_account_id(cls):
        api_call = APICall(token_type=cls.read_access_token, endpoint='account', version='3', params={}, headers={})
        json_response = api_call.make_request()
        if 'id' in json_response:
            cls.account_id = json_response['id']
            print(f"Successfully retrived account id: {cls.account_id}")
            return
        print("Error. Could not retrieve account id.")
    
    @classmethod
    def get_req_token(cls):
        api_call = APICall(cls.read_access_token, endpoint="auth/request_token", version='4', params={}, headers={})
        response = api_call.send_data()
        if response['success'] == True:
            request_token = response['request_token']
            print("Successfully retrieved request token")
            return request_token
        print(f"Error retrieving request token: {response['status_message']}")

    @classmethod
    def approve_req_token(cls, request_token):
        print(f"Approve your request token by visiting: https://www.themoviedb.org/auth/access?request_token={request_token}")
        input("Press enter when finished to continue:")

    @classmethod
    def get_access_token(cls, request_token):
        payload = {"request_token": request_token}
        api_call = APICall(cls.read_access_token, "auth/access_token", '4', {}, {}, data=payload)
        response = api_call.send_data()
        if response['success'] == True:
            access_token = response['access_token']
            print("Successfully retrieved access token")
            return access_token
        print(f"Error retrieving access token: {response['status_message']}")

    @staticmethod
    def update_config(config_secrets, access_token):
        config_secrets['tmdb_write_access_token'] = access_token
        with open("secrets.yaml", "w") as config_yml:
            yaml.safe_dump(config_secrets, config_yml)
            print("Saved access token to yaml config file.")

    @classmethod
    def get_tokens(cls, config_secrets):
        request_token = cls.get_req_token()
        cls.approve_req_token(request_token)
        access_token = cls.get_access_token(request_token)
        cls.write_access_token = access_token
        cls.update_config(config_secrets, access_token)

# This class is meant to get the TMDB id's for each movie in the watched list,
# so that we can add them to a custom TMDB list, for which we need the id of each movie.
class TMDBMovieIDs(TMDBCredentials):
    def __init__(self, watched_movies_file, tmdb_movie_ids_file):
        self.watched_movies_file = watched_movies_file
        self.tmdb_movie_ids_file = tmdb_movie_ids_file

    def get_watched_movies(self):
        with open(self.watched_movies_file, "r", encoding = 'utf-8') as movies_csv:
            # Add all movies from csv to watched_movies list as a dictionary
            watched_movies = []
            movies = csv.DictReader(movies_csv, delimiter = ";")
            for movie in movies:
                del movie['Letterboxd URI'] # Get rid of URI key, as it is not relevant
                watched_movies.append(movie)
        return watched_movies

    def get_tmdb_movie_ids(self, watched_movies): 
        # Method to fetch any matches for watched movies, then filter out any fuzzy matches,
        # and save the tmdb id's for the exact matches along with the movie names

        raw_tmdb_movie_ids = {} # Results go in this dictionary

        for movie_dict in watched_movies:
            movie_name = movie_dict['Name']
            movie_year = movie_dict['Year'] 
            params = {"query": movie_name,
                    "year": movie_year} # Params object to be used in GET request to tmdb server
                    
            callone = APICall(TMDBCredentials.read_access_token, 'search/movie', '3', params, {}, None)
            json_response = callone.make_request()
            results_list = json_response['results']
            if len(results_list) == 0: # Check length of list. If 0, then no matches were found
                print(f"No results for {movie_name}")
                time.sleep(1.0)
                continue
            if len(results_list) == 1: 
                # If length of results list is 1, then 1 unique match was found for current movie
                # Save that movie and it's returned tmdb id to the raw_tmdb_movies_ids dictionary
                print(f"1 unique result for {movie_name}")
                movie_id = results_list[0]['id']
                raw_tmdb_movie_ids[movie_id] = movie_name
                time.sleep(1.0)
                continue
            # If both above if statements return false, then results list is longer than 1,
            # thus multiple matches were found for the current movie
            print(f"Filtering multiple results for {movie_name}")
            for result_dictionary in results_list:
                # We want to filter out all fuzzy matches/non-exact matches,
                # so we iterate over the multiple result dictionaries in the results list
                # and skip any results/matches where the returned movie's title/name,
                # was not an exact match to the movie_name used in the GET request
                returned_movie_name = result_dictionary['title']
                movie_id_2 = result_dictionary['id']
                if movie_name != returned_movie_name:
                    continue
                # We only save non fuzzy matches to our raw_tmdb_movie_ids dictionary,
                # and filter out/skip all the fuzzy matches, leaving us with a dictionary containing,
                # mostly unique matches, besides some edge cases which we will handle separately later
                raw_tmdb_movie_ids[movie_id_2] = movie_name 
            time.sleep(1.0)
        return raw_tmdb_movie_ids
    
    def save_movies(self, raw_tmdb_movie_ids): 
        # Save results to json files for persistence and further processing + filtering
        with open(self.tmdb_movie_ids_file, "w") as unique_movies_json:
            json.dump(raw_tmdb_movie_ids, unique_movies_json, indent = 4)
            print("Movies successfully saved.")

    def get_and_save_movies(self): # Single method to do everything with one call
        watched_movies = self.get_watched_movies()
        raw_tmdb_movie_ids = self.get_tmdb_movie_ids(watched_movies)
        self.save_movies(raw_tmdb_movie_ids)

    @staticmethod
    def load_returned_movies(tmdb_movie_ids_file):
        with open(tmdb_movie_ids_file, "r") as unique_movies_json:
            unique_movies = json.load(unique_movies_json)
        return unique_movies
    
class TMDBLists(TMDBCredentials):
    @classmethod
    def get_all_list_ids(cls):
        tmdb_list_ids = {}
        api_call = APICall(cls.read_access_token, f"account/{cls.account_id}/lists", '3', {}, {}, None)
        json_response = api_call.make_request()
        results_list = json_response['results']
        if len(results_list) == 0:
            print(f"This user has no lists.")
            return
        if len(results_list) == 1:
            list_id = results_list[0]['id']
            list_name = results_list[0]['name']
            tmdb_list_ids[list_id] = list_name
            return tmdb_list_ids  # Return the dictionary with the one list
        for user_list in results_list:
            this_list_id = user_list['id']
            this_list_name = user_list['name']
            tmdb_list_ids[this_list_id] = this_list_name
        return tmdb_list_ids
    
    @staticmethod
    def get_list_id_by_name(list_name, tmdb_list_ids):
        list_id = None
        list_names_lower = [lowercase_list_name.lower() for lowercase_list_name in tmdb_list_ids.values()]
        if list_name not in list_names_lower:
            print(f"{list_name} does not exist. Check for possible typo's and try again.")
            return # Exit method if the specified list does not exist
        for id_of_list, name_of_list in tmdb_list_ids.items():
            if name_of_list.lower() != list_name:
                continue
            # If user specified list name is equal to name value of an id in the tmdb_list_ids dictionary,
            # then assign that id to be the list_id variable that we use in our api call
            list_id = id_of_list
            break # End for loop once the list_id has been found
        return list_id
    
    @staticmethod
    def get_and_check_user_list_input(tmdb_list_ids):
        while True:
            list_names_lower = [name_of_list.lower() for name_of_list in tmdb_list_ids.values()]
            print("All of your TMDB lists:")
            for list_name in tmdb_list_ids.values():
                print(f"- {list_name}")
            user_list = input("Please choose a list to add your movies to: ").lower()
            if user_list not in list_names_lower:
                print("Invalid list name. Please choose from one of the above lists.")
                continue
            break
        return user_list
    
    @classmethod
    def add_movies_to_list(cls, list_name, list_id, tmdb_movie_ids_file):
        movie_ids = TMDBMovieIDs.load_returned_movies(tmdb_movie_ids_file)
        payload = {'items': []}
        for movie_id in movie_ids:
            movie_id_dictionary = {}
            movie_id_dictionary['media_type'] = 'movie' # Create media type key and assign it to be movie, for every movie id
            movie_id_dictionary['media_id'] = movie_id # Assign movie id key from json file to be the media_id key value
            payload['items'].append(movie_id_dictionary) # add each dictionary created for each movie id to the items list
        api_call = APICall(cls.write_access_token, f"list/{list_id}/items", '4', {}, {}, data = payload)
        json_response = api_call.send_data()
        if json_response['success'] == True:
            print(f"Movies successfully added to {list_name.title()}!")
            return
        status_msg = json_response['status_message']
        print(f"Error adding movies to {list_name} list: {status_msg}")