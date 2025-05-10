import csv
import time
from classes import APICall
from dotenv import load_dotenv
import json

# This script is meant to get the TMDB id's for each movie in my letterboxd watched list,
# so that I can add them to a custom TMDB list, for which I need the id of each movie.

load_dotenv()

unique_movies_path = "unique_movies.json"
duplicate_movies_path = "duplicate_movies.json"

letterboxd_watched= "letterboxd_data/watched.csv"

write_token = "tmdb_write_access_token"

def get_watched_movies():
    with open(letterboxd_watched, "r", encoding = 'utf-8') as movies_csv:
        # Add all movies from csv to watched_movies list as a dictionary
        watched_movies = []
        movies = csv.DictReader(movies_csv, delimiter = ";")
        for movie in movies:
            del movie['Letterboxd URI'] # Get rid of URI key, as it is not relevant
            watched_movies.append(movie)
    return watched_movies

def get_movie_ids(watched_movies):
    movie_ids_dict = {} # Unique movies and their id's go here
    duplicate_movies = [] # Any movies with multiple results go here for further processing and filtering later

    for movie_dict in watched_movies:
        movie_name = movie_dict['Name']
        movie_year = movie_dict['Year'] 
        params = {"query": movie_name,
                "year": movie_year}
        
        callone = APICall(write_token, 'search/movie', '3', params, {}, None)
        json_response = callone.make_request()
        results_list = json_response['results']
        if len(results_list) == 0: # If no results are found, then print message and continue to next movie
            print(f"No results for {movie_name}")
            time.sleep(1.0)
            continue
        if len(results_list) > 1: 
            # If result list is longer than 1, then there are multiple results for the movie query,
            # thus we add results to the duplicate_movies list as a dictionary
            for result in results_list:
                dup_movie_dict = {}
                dup_movie_name = result['title']
                dup_movie_release_date = result['release_date']
                dup_movie_id = result['id']
                dup_movie_dict[dup_movie_id] = [dup_movie_name, dup_movie_release_date] 
                duplicate_movies.append(dup_movie_dict)
            time.sleep(1.0)
            continue
        # If results list is neither empty nor longer than 1 item, then we have 1 unique result for the movie,
        # thus we can safely save it and it's id to the movie_ids_dict dictionary
        results_dict = results_list[0]
        movie_id = results_dict['id']
        movie_ids_dict[movie_name] = movie_id
        time.sleep(1.0)
    return movie_ids_dict, duplicate_movies

watched_movies = get_watched_movies()
# Unpack tuple returned by get_movie_ids function, to get the unique movies dictionary,
# and the duplicate_movies list.
unique_movies, duplicate_movies = get_movie_ids(watched_movies)

def save_movies(unique_movies, duplicate_movies): 
    # Save results to json files for persistence and further processing + filtering
    with open(unique_movies_path, "w") as unique_movies_json:
        json.dump(unique_movies, unique_movies_json, indent = 4)
        print("Unique movies successfully saved.")

    with open(duplicate_movies_path, "w") as dup_movies_json:
        json.dump(duplicate_movies, dup_movies_json, indent = 4)
        print("Duplicate movies successfully saved.")

save_movies(unique_movies, duplicate_movies)