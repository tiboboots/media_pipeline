import sys
from pathlib import Path
from movies_to_tmdb import TMDBMovieIDs, TMDBLists, TMDBCredentials

config_secrets = TMDBCredentials.get_secrets_config() # Get yaml config file

if TMDBCredentials.write_access_token is None: # Check if write access token has been set
    TMDBCredentials.get_tokens(config_secrets) # If not, then fetch the users write acccess token

TMDBCredentials.get_account_id() # Get users account id once tokens and credentials have been set

script_path = Path(__file__) # Get path to script

project_directory = script_path.parent.parent # Get path to project root directory relative to script location at runtime

watched_movies_file = project_directory / "movies-data" / "watched.csv" # Build path for watched movies csv file

tmdb_movie_ids_file = project_directory / "tmdb_movie_ids.json" # Build path for movie ids json file 

movies_dir = project_directory / "movies-data" # Build path to the movies-data directory

if not movies_dir.exists():
    print(f"{movies_dir} does not exist. Please create the movies-data directory first.")
    print("Then add a csv file containing your watched movies list to it. Try again afterwards.")
    sys.exit(1)

if not watched_movies_file.exists():
    print(f"No watched movies csv file found at {watched_movies_file}")
    print(f"There should be a csv file found in the movies-data directory containing your watched movies.")
    print(f"Please try again once you have added the file.")
    sys.exit(1)

my_lists = TMDBLists() # Create TMDBLists instance

all_list_ids = my_lists.get_all_list_ids() # Get the id's for all the user's lists, and their names

# Ask user to choose a list to add movies to, return that list for later use
list_name = my_lists.get_and_check_user_list_input(tmdb_list_ids = all_list_ids)

movie_ids = TMDBMovieIDs() # Create TMBDMovieIDs object

movie_ids.get_and_save_movies() # Get all tmdb id's for movies in watched.csv file and save them locally

# Use list name specified by user, saved as the list_name variable, to get the id for that list
list_id = my_lists.get_list_id_by_name(list_name = list_name, tmdb_list_ids = all_list_ids)

# Add all movies from user watched list csv file to the specified list, using it's id
my_lists.add_movies_to_list(list_name = list_name, list_id = list_id)
