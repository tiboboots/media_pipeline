import csv
from classes import APICall

letterboxd_watched= "letterboxd_data/watched.csv"

with open(letterboxd_watched, "r", encoding = 'utf-8') as movies_csv:
    # Add all movies from csv to watched_movies list as a dictionary
    watched_movies = {"Movies": []}
    movies = csv.DictReader(movies_csv, delimiter = ";")
    for movie in movies:
        del movie['Letterboxd URI'] # Get rid of URI key, as it is not relevant
        watched_movies["Movies"].append(movie) # append each movie dictionary to list in watched_movies