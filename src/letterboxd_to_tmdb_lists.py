import csv
import time
from dotenv import load_dotenv
import json
from api_call_class import APICall

load_dotenv()

class TMDBCredentials:
    read_access_token = "tmdb_read_access_token"
    write_access_token = "tmdb_write_access_token"
    account_id = None

    @classmethod
    def get_account_id(cls):
        api_call = APICall(cls.read_access_token, 'account', '3', {}, {}, None)
        json_response = api_call.make_request()
        cls.account_id = json_response['id']

# Due to limited detail in exported letterboxd data, some manual filtering is required for rare duplicate edge cases,
# where the name and release year are the exact same.

# This class is meant to get the TMDB id's for each movie in my letterboxd watched list,
# so that I can add them to a custom TMDB list, for which I need the id of each movie.
class TMDBMovieIDs(TMDBCredentials):
    def __init__(self):
        self.unique_movies_path = "unique_movies.json"
        self.watched_movies_path= "letterboxd_data/watched.csv"
        self.token_type = self.read_access_token

    def get_watched_movies(self):
        with open(self.watched_movies_path, "r", encoding = 'utf-8') as movies_csv:
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
                    
            callone = APICall(self.token_type, 'search/movie', '3', params, {}, None)
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
        with open(self.unique_movies_path, "w") as unique_movies_json:
            json.dump(raw_tmdb_movie_ids, unique_movies_json, indent = 4)
            print("Movies successfully saved.")

    def get_and_save_movies(self): # Single method to do everything with one call
        watched_movies = self.get_watched_movies()
        raw_tmdb_movie_ids = self.get_tmdb_movie_ids(watched_movies)
        self.save_movies(raw_tmdb_movie_ids)

    def load_returned_movies(self):
        with open(self.unique_movies_path, "r") as unique_movies_json:
            unique_movies = json.load(unique_movies_json)
        return unique_movies
    
class TMDBLists(TMDBCredentials):
    def __init__(self):
        self.token_type = self.read_access_token
        self.lists_endpoint = f"/account/{self.account_id}/lists"
        self.tmdb_list_ids = {}

    def get_list_ids(self):
        api_call = APICall(self.token_type, self.lists_endpoint, '3', {}, {}, None)
        json_response = api_call.make_request()