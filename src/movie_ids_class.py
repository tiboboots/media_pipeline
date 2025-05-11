import csv
import time
from dotenv import load_dotenv
import json
from api_call_class import APICall

load_dotenv()

# This class is meant to get the TMDB id's for each movie in my letterboxd watched list,
# so that I can add them to a custom TMDB list, for which I need the id of each movie.
class MovieIDs:
    def __init__(self):
        self.unique_movies_path = "unique_movies.json"
        self.duplicate_movies_path = "duplicate_movies.json"
        self.watched_movies_path= "letterboxd_data/watched.csv"
        self.write_token = "tmdb_write_access_token"

    def get_watched_movies(self):
        with open(self.watched_movies_path, "r", encoding = 'utf-8') as movies_csv:
            # Add all movies from csv to watched_movies list as a dictionary
            watched_movies = []
            movies = csv.DictReader(movies_csv, delimiter = ";")
            for movie in movies:
                del movie['Letterboxd URI'] # Get rid of URI key, as it is not relevant
                watched_movies.append(movie)
        return watched_movies

    def get_movie_ids(self, watched_movies):
        movie_ids_dict = {} # Unique movies and their id's go here
        duplicate_movies = {} # Any movies with multiple results go here for further processing and filtering later

        for movie_dict in watched_movies:
            movie_name = movie_dict['Name']
            movie_year = movie_dict['Year'] 
            params = {"query": movie_name,
                    "year": movie_year}
            
            callone = APICall(self.write_token, 'search/movie', '3', params, {}, None)
            json_response = callone.make_request()
            results_list = json_response['results']
            if len(results_list) == 0: # If no results are found, then print message and continue to next movie
                print(f"No results for {movie_name}")
                time.sleep(1.0)
                continue
            if len(results_list) > 1: 
                print(f"Multiple results found for {movie_name}, saving all...")
                # If result list is longer than 1, then there are multiple results for the movie query,
                # thus we add results to the duplicate_movies list as a dictionary
                for result in results_list:
                    dup_movie_name = result['title']
                    dup_movie_release_date = result['release_date']
                    dup_movie_id = result['id']
                    duplicate_movies[dup_movie_id] = [dup_movie_name, dup_movie_release_date] 
                time.sleep(1.0)
                continue
            # If results list is neither empty nor longer than 1 item, then we have 1 unique result for the movie,
            # thus we can safely save it and it's id to the movie_ids_dict dictionary
            print(f"Saving 1 result for {movie_name}...")
            results_dict = results_list[0]
            movie_id = results_dict['id']
            movie_ids_dict[movie_name] = movie_id
            time.sleep(1.0)
        return movie_ids_dict, duplicate_movies

    def save_movies(self, unique_movies, duplicate_movies): 
        # Save results to json files for persistence and further processing + filtering
        with open(self.unique_movies_path, "w") as unique_movies_json:
            json.dump(unique_movies, unique_movies_json, indent = 4)
            print("Unique movies successfully saved.")

        with open(self.duplicate_movies_path, "w") as dup_movies_json:
            json.dump(duplicate_movies, dup_movies_json, indent = 4)
            print("Duplicate movies successfully saved.")

    def load_unique_movies(self):
        with open(self.unique_movies_path, "r") as unique_movies_json:
            unique_movies = json.load(unique_movies_json)
        return unique_movies
    
    def load_duplicate_movies(self):
        with open(self.duplicate_movies_path, "r") as dup_movies_json:
            duplicate_movies = json.load(dup_movies_json)
        return duplicate_movies

    def get_and_save_movies(self): # Single method to do everything with a single call
        watched_movies = self.get_watched_movies()
        unique_movies, duplicate_movies = self.get_movie_ids(watched_movies)
        self.save_movies(unique_movies, duplicate_movies)