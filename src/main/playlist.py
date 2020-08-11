import os 
import sys
import json
import pprint
import logging 

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
info_dir = os.path.join(base_dir, 'info')
melon_dir = os.path.join(info_dir, 'melon_data')
spotify_dir = os.path.join(info_dir, 'spotify_data')
sys.path.append(base_dir)

from helpers import others_help, api_help, tokens_help, decorators
from main import spotify_run, melon_data

logger = logging.getLogger('main_logger')
d_logger = logging.getLogger('display_logger')

module_name = 'playlist.py'

@decorators.main_logger(module_name)
def get_set_playlists(): 
    """
    Preset playlist names and descriptions as corresponding to Melon chart categories 
    Accepts no params 
    Returns playlists as dic of chart_category:(name, description) key:val pairs 
    """

    playlists = {}

    categories = melon_data.get_categories() 
    for category in categories: 
        name = f'Top Songs In South Korea: {category.capitalize()}'
        description = f"Enjoy the top songs listened to by South Koreans :)"
        playlists[category] = (name, description) 
    
    return playlists 

@decorators.main_logger(module_name)
def save_playlist_info(playlist_info): 
    """
    Saves important information about playlist post-creation 
    Accepts dict of category:playlist-info key:value pairs 
    Returns None 
    """
    if others_help.file_contents(spotify_dir, 'playlist-info.json', data=playlist_info) is None: 
        raise Exception('Failed to save playlist post-processing information.')

@decorators.main_logger(module_name)
def create_playlists(): 
    """
    Creates spotify playlists with preset playlist names and descriptions, saves important information to info dir
    Accepts no params 
    Returns None 
    """

    tokens_help.refresh_token() # refreshes token // token expires very quickly (~1 hr), assuming user is not spamming, justified to do so

    access_token, _ = tokens_help.get_tokens() 

    content_type = 'application/json'

    headers = {
        'Authorization': f'Authorization: Bearer {access_token}', 
        'Content-Type': content_type, 
    }

    user_id = spotify_run.get_id() 

    endpoint = f'https://api.spotify.com/v1/users/{user_id}/playlists'

    playlists = get_set_playlists() 

    playlist_info = {} 

    for category in playlists: 
        name, description = playlists.get(category) 

        data = {
            'name': name, 
            'description': description,
        }

        data = json.dumps(data)

        response = api_help.requests_general('post', endpoint, data=data, headers=headers)

        playlist_info[category] = response.get('uri')            

    return playlist_info 

@decorators.main_logger(module_name)
def get_playlist_ids(): 
    """
    Gets playlist ids 
    No params 
    Returns dictionary of playlist ids 
    """

    playlist_info = others_help.file_contents(spotify_dir, 'playlist-info.json')
    if playlist_info is None: raise Exception('Error trying to load playlist-info.json.')
    
    for category in playlist_info: 
        uri = playlist_info[category]
        playlist_id = uri.split(':')[-1]
        playlist_info[category] = playlist_id 
    
    return playlist_info 

@decorators.main_logger(module_name)
def save_results(search_results, postfix): 
    """
    Saves user search results 
    Accepts dict of search results and string postfix param for file 
    Returns None 
    """

    for category in search_results: 
        if others_help.file_contents(melon_dir, f'{category}-{postfix}.json', data=search_results[category]) is None: 
            raise Exception(f'Error saving search results for {category}.')

@decorators.main_logger(module_name)
def save_preferences(preferences): 
    """
    Save user preferences for search results 
    Accepts required dic param of song:uri, artist:proper artist name key formats 
    Returns None 
    ...
    """

    content = None 

    if os.path.exists(os.path.join(melon_dir, 'preferences.json')): # content is not None if both file exists AND file has content 
        content = others_help.file_contents(melon_dir, 'preferences.json')

    if content is None: 
        content = preferences 
    else: # add to content from file 
        for preference in preferences: # both song and artist preferences 
            if content.get(preference, None) is not None: 
                content[preference] = preferences[preference]
    
    if others_help.file_contents(melon_dir, 'preferences.json', data=content) is None: 
        raise Exception('Error saving preferences.')

@decorators.main_logger(module_name) 
def get_preferences(): 
    """
    Gets user preferences for search reuslts 
    No params 
    Returns preferences if preferences else None 
    """

    if not os.path.exists(os.path.join(melon_dir, 'preferences.json')):
        return None 
    
    try: 
        with open(os.path.join(melon_dir, 'preferences.json')) as f: 
            content = json.loads(f.read())
    except:
        return None 
    
    return content 

@decorators.main_logger(module_name) 
def clear_preferences(): 
    """
    Clear user preferences 
    No params 
    Returns True if successful else None 
    """

    with open(os.path.join(melon_dir, 'preferences.json'), 'w'): 
        pass 
    
    return True 

@decorators.main_logger(module_name)
def process_help(category, results): 
    """
    Helps with processing songs in process_results() 
    Accepts string param of category and array param of results (all uris)
    Returns 
    """

    songs = results['CERTAIN']

    savable = {} 

    processed = {
        'exceptions': False, 
        'uncertain': False, 
    }

    while True: 

        msg = 'Process "exceptions" or "uncertain", or "done"? '
        choice2 = others_help.validate_choices(['exceptions', 'uncertain', 'done'], msg=msg)

        if choice2 in ['exceptions', 'uncertain']: 

            if len(results[choice2.upper()]) == 0: 
                print(f'There is nothing to parse in "{choice2}". ')
                continue
            if processed.get(choice2): 
                msg = 'You have already processed this before. Again (yes) or (no)? '
                reprocess = others_help.validate_choices(['yes', 'no'], msg=msg)
                if reprocess == 'yes': 
                    processed[choice2] = True 
                else:
                    continue  

            for result in results[choice2.upper()]: 

                if choice2 == 'exceptions': 
                    others_help.print_contents(result[0]) # REQUESTED: ...
                    track, name = result[1] 
                    choice3 = others_help.validate_choices(['search', 'pass', 'done'])
                else: 
                    song_info = {
                        'Found': result[0], 
                        'Requested': result[1], 
                    }
                    song_details = result[2]
                    track, name, song_uri = song_details
                    found_name = result[3] 

                    others_help.print_contents(song_info)

                    choice3 = others_help.validate_choices(['add', 'search', 'pass', 'done'])
                
                # validate_choices does validation to ensure 'add' is not allowed for 'exceptions'
                if choice3 == 'add': 
                    songs.append(song_uri)
                    savable[track] = song_uri 
                    savable[name] = found_name 
                elif choice3 == 'search': 
                    manual_uri, artists = spotify_run.manual_search_track() 
                    if manual_uri: 
                        songs.append(manual_uri)
                        savable[track] = manual_uri 
                        if len(artists) == 1: # only works as is for singular artists 
                            savable[name] = artists[0]
                elif choice3 == 'done': 
                    processed[choice2] = True 
                    break

        elif choice2 == 'done':

            if len(savable) > 0: 
                msg = 'Save your choices (yes) or (no)? '
                if others_help.validate_choices(['yes', 'no'], msg=msg) == 'yes': 
                    save_preferences(savable)

            processed = {
                category: songs, 
            }

            save_results(processed, 'post-results')

            break

    return True 
    
@decorators.main_logger(module_name)
def process_results(select): 
    """
    User parses search results 
    Accepts array of user's selected charts 
    Returns None 
    """

    for category in select: 

        results = others_help.file_contents(melon_dir, f'{category}-pre-results.json')
        if not results: raise Exception(f'Error trying to load {category}-pre-results.json.')

        msg = f"""
            For "{category}" category there are... \n
            {len(results['CERTAIN'])} Certains \n
            {len(results['EXCEPTIONS'])} Exceptions \n
            {len(results['UNCERTAIN'])} Uncertains \n
            What do you want to do... "process" or "pass" (just keep certains)? 
        """
        choice = others_help.validate_choices(['process', 'pass'], msg=msg)
        
        if choice == 'pass': 

            processed = {
                category: results['CERTAIN'],
            }

            save_results(processed, 'post-results')

        else: 

            if process_help(category, results) is None: 
                raise Exception(f'Failed to process results for "{category}" category.')
            

@decorators.main_logger(module_name)
def get_processed_results(select): 
    """
    Get parsed results 
    No params 
    Returns dict of chart:CERTAIN uris  
    """

    uris = {} 

    for category in select: 
        category_uris = others_help.file_contents(melon_dir, f'{category}-post-results.json') 
        if category_uris is None: raise Exception(f'Error loading results for {category}-post-results.json.')
        
        uris[category] = category_uris 

    return uris 

@decorators.main_logger(module_name)
def put_playlists(select=None): 
    """
    Adds playlist items to generated spotify playlists 
    Accepts optional array of which categories to place songs into 
    Returns True if successful else None  
    """

    playlist_ids = get_playlist_ids()

    print('put_playlists(): Gathering uris for tracks...')

    if not select: 
        select = [category for category in melon_data.get_categories()]
    
    processed = []
    for category in select: 
        msg = f'Do you want to process "{category}" (yes) or (no)? '
        if others_help.validate_choices(['yes', 'no'], msg=msg) == 'yes': 
            search_results = spotify_run.search_tracks([category]) 
            save_results(search_results, 'pre-results')
            process_results([category])
            processed.append(category)

    if len(processed) == 0: 
        raise Exception('Must process at least one category of songs.')

    uris = get_processed_results(processed)

    tokens_help.refresh_token()
    access_token, _ = tokens_help.get_tokens()
    headers = {
        'Authorization': f'Authorization: Bearer {access_token}',
    }

    print('put_playlists(): Adding top songs for charts...')

    for chart in processed: 
        playlist_id = playlist_ids.get(chart, None) 
        playlist_uris = uris.get(chart, None) 
        
        if not all([playlist_id, playlist_uris]): 
            raise Exception(f'{chart} is not a valid chart category or is not in list of playlist uris.')

        playlist_uris = ','.join(playlist_uris)
            
        endpoint = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks?uris={playlist_uris}'

        api_help.requests_general('put', endpoint=endpoint, headers=headers)

        print(f'Top Songs added for... "{chart}" chart')
    
    return True 

@decorators.main_logger(module_name)
def main_create(): 
    """
    Handles creation of playlists  
    Accepts no params
    Returns True if successful else None  
    """

    playlist_info = create_playlists() 

    save_playlist_info(playlist_info)

    return True 
    
@decorators.main_logger(module_name)
def main_both(): 
    """
    Handles creation AND population of playlists 
    Accepts no params
    Returns True if successful else None  
    """

    main_create() 

    put_playlists()

    return True 

if __name__ == '__main__': 
    select = [category for category in melon_data.get_categories()]
    process_results(select)