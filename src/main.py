from movies_to_tmdb import TMDBMovieIDs, TMDBLists, TMDBCredentials, FilePaths

config_secrets = TMDBCredentials.get_secrets_config() # Get yaml config file

if TMDBCredentials.write_access_token is None: # Check if write access token has been set
    TMDBCredentials.get_tokens(config_secrets) # If not, then fetch the users write acccess token

TMDBCredentials.get_account_id() # Get users account id once tokens and credentials have been set

all_list_ids = TMDBLists.get_all_list_ids() # Get the id's for all the user's lists, and their names

# Ask user to choose a list to add movies to, return that list for later use
list_name = TMDBLists.get_and_check_user_list_input(tmdb_list_ids = all_list_ids)

paths = FilePaths.load_paths_yaml() # Load the paths.yaml file to get all file paths

# Set all file paths if they have not been set already, if path to movies csv has not yet been set,
# then user will be prompted to specify the path to their csv file containing their movies, which is then saved
TMDBMovieIDs.set_file_paths(paths) 

TMDBMovieIDs.get_and_save_movies() # Get all tmdb id's for movies in csv file and save them locally

# Use list name specified by user, saved as the list_name variable, to get the id for that list
list_id = TMDBLists.get_list_id_by_name(list_name = list_name, tmdb_list_ids = all_list_ids)

# Add all movies from user watched list csv file to the specified list, using it's id
TMDBLists.add_movies_to_list(list_name = list_name, list_id = list_id)
