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
from main import melon_data, playlist

logger = logging.getLogger('main_logger')
d_logger = logging.getLogger('display_logger')

module_name = 'spotify_run.py'

@decorators.main_logger(module_name)
def get_id(): 
    """
    Gets the spotify user id 
    No params
    Returns string of spotify user id 
    """
    
    tokens_help.refresh_token() # token access lasts only 1 hr for Spotify API 

    access_token, _ = tokens_help.get_tokens() 

    endpoint = 'https://api.spotify.com/v1/me'

    headers = {
        'Authorization': f'Authorization: Bearer {access_token}',
    }

    response = api_help.requests_general('get', endpoint, headers=headers)

    user_id = response.get('id', None) 

    if not user_id: 
        raise Exception('User id missing in response in user_id().')
    
    return user_id

@decorators.main_logger(module_name)
def auto_search_track(track): 
    """
    Get response of track search -- DRY 
    Accepts string param of track 
    Returns response 
    """

    tokens_help.refresh_token() 

    access_token, _ = tokens_help.get_tokens() 

    track_form = '%20'.join(track.split())

    item_type = 'track'

    endpoint = f'https://api.spotify.com/v1/search?q={track_form}&type={item_type}'

    headers = {
        'Authorization': f'Authorization: Bearer {access_token}'
    }

    response = api_help.requests_general('get', endpoint, headers=headers)

    return response 

@decorators.main_logger(module_name)
def manual_search_track(track=''): 
    """
    Find the track MANUALLY 
    Accepts string param of track 
    Returns None     
    """

    prefill = True 

    while True: 

        msg = 'Enter track name to search [track_name, number_results(=3)]: '
        if prefill: 
            search_req = others_help.prefill_input(msg, track)
        else: 
            search_req = str(input(msg))

        search_req = search_req.split(',') # comma because track names can have spaces 
        if len(search_req) == 0 or search_req is None:
            others_help.print_error('No search param given.')
            continue 
        track_name = search_req[0].strip()
        num_results = 3
        if len(search_req) > 1: 
            num_results = int(search_req[1])
        if num_results <= 0: 
            others_help.print_error('Invalid number of results, reset to default of 3.')
            num_results = 3

        response = auto_search_track(track_name) 

        items = response['tracks']['items']

        result = {} 

        display = {}

        for i in range(num_results): 
            try:
                item = items[i]
                album = item['album']
                album.pop('available_markets')
                album.pop('images')
                result[i] = item
                artists = [artist['name'] for artist in album['artists']]
                name = album['name']
                display[i] = {
                    'Name': name,  
                    'Artists': artists, 
                }
            except: 
                pass 

        if len(display) == 0: 
            display = "NO MATCHING RESULTS."

        pprint.pprint(display) 

        msg = 'Number of matching song, "retry(-x for no prefill)", "pass", or "block": '
        chosen = str(input(msg))

        if chosen == 'retry': 
            pass 
        elif chosen == 'retry-x': 
            prefill = False 
        elif chosen == 'pass': 
            return (False, None, None)
        elif chosen == 'block': 
            return (True, None, None)
        else: 
            num = int(chosen)
            if not num in list(range(num_results)): 
                others_help.print_error('manual_search_track(): Incorrect input.')
                pass 
            else: 
                if not result[num].get('uri', None): 
                    others_help.print_error('manual_search_track(): Result does not have track uri or idx entered for no search results.')

                return (False, result[num]['uri'], display[num]['Artists'])

@decorators.main_logger(module_name)
def search_track(track, artist): 
    """
    Searches for requested track with matching artist to given artist 
    Accepts string params of track and artist 
    Returns likely track id else None 
    """

    # if track is in preferences dic already (that is, if preferences exist)
    preferences = playlist.get_preferences() 
    if preferences is not None: 
        saved_preferences = preferences['desired']
        saved_uri = saved_preferences.get(track, None) 
        saved_artist = saved_preferences.get(artist, None) 

        blacklist = preferences['blacklist']
        blacklist_track = blacklist.get(track, None)
    else: 
        saved_uri = saved_artist = blacklist_track = None 
    if saved_uri is not None: 
        return (False, False, True, 0, 0, (0, 0, saved_uri), 0)
    if blacklist_track is not None: 
        return (True, False, False, 0, 0, (0, 0, saved_uri), 0)

    response = auto_search_track(track) 

    # check for Melon's odd artist formatting
    artist1, artist2 = artist, 'nonsense-placeholder'
    artist_form = artist.split('(')
    if len(artist_form) > 1: 
        artist1 = artist_form[0].strip()
        artist2 = artist_form[1][:-1].strip() # remove ) 

    # return response

    try: 
        first = response['tracks']['items'][0]
        creator = first['album']['artists'][0]['name']
        track_id = response['tracks']['items'][0]['uri']
        track_name = first['name']

        artists = [artist1, artist2, saved_artist]
        certainty = True if any(creator == name for name in artists) else False 
    except: 
        return (False, True, f'{track} by {artist}', (track,artist)) # (track, artist) for saving preferences
    
    return (False, False, certainty, f'{track_name} by {creator}', f'{track} by {artist}',(track, artist, track_id), creator) # (track_id, track, artist) for saving preferences

@decorators.main_logger(module_name)
def search_tracks(select=None): 
    """
    Responds with uris of tracks found in all or specified melon chart categories
    Accepts optional array of melon chart name ('day', 'hits', 'month', 'week')
    Returns dict of melon chart name:all found track uris
    """

    all_tracks = melon_data.get_tops(select)   

    if not select: 
        select = melon_data.get_categories() 

    search_results = {} 

    for chart in select: 

        others_help.print_alert(f'search_tracks(): Beginning search for uris in "{chart}" chart...')

        tracks = all_tracks[chart]

        search_results[chart] = {
            'CERTAIN': [],
            'UNCERTAIN': [],
            'EXCEPTIONS': [],
        }

        for title, artist in tracks.items(): 

            search_result = search_track(title, artist) 

            if search_result[0]: # blacklist 
                continue

            if search_result[1]: # exception
                search_results[chart]['EXCEPTIONS'].append((search_result[2],search_result[3])) 

            else: 
                _, _, certainty, found, request, track_details, found_name = search_result 
                track, artist, track_id = track_details

                if certainty: 
                    search_results[chart]['CERTAIN'].append(track_id)

                else: 
                    search_results[chart]['UNCERTAIN'].append((found, request, track_details, found_name))
        
        others_help.print_alert(f'search_tracks(): DONE search for uris in "{chart}" chart...')
    
    others_help.print_alert(f'search_tracks(): FINISHED search for all uris...')

    return search_results

@decorators.main_logger(module_name)
def refresh(): 
    """
    Refreshes top songs list and generates playlists 
    No params 
    Returns True if successful else None  
    """

    tokens_help.refresh_token() 

    melon_data.main_create() 

    playlist.put_playlists()

    return True 

if __name__ == '__main__': 
    print(manual_search_track())