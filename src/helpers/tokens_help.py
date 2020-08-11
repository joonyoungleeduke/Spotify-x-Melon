import os 
import json 
import sys 
import requests 
import logging 

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
info_dir = os.path.join(base_dir, 'info')
spotify_dir = os.path.join(info_dir, 'spotify_data')
sys.path.append(base_dir) 

from helpers import others_help, api_help, decorators

logger = logging.getLogger('main_logger')
d_logger = logging.getLogger('display_logger')

module_name = 'tokens_help.py'

@decorators.main_logger(module_name)
def get_tokens(): 
    """
    Gets auth and refresh tokens if existing 
    No params
    Returns string of auth and refresh tokens 
    """

    if not os.path.exists(os.path.join(spotify_dir, 'spotify-tokens.json')):
        raise Exception('Spotify-tokens.json does not exist.')

    with open(os.path.join(spotify_dir, 'spotify-tokens.json')) as tokens_file: 
        tokens = json.loads(tokens_file.read())
    
    access_token = tokens.get('access_token', None) 
    refresh_token = tokens.get('refresh_token', None) 

    if not refresh_token or not access_token: 
        raise Exception('Refresh or access token key does not exist in spotify-tokens.json.')

    return (access_token, refresh_token)

@decorators.main_logger(module_name)
def post_tokens(tokens=None): 
    """
    Post access and refresh tokens to relevant file 
    Accepts dic of tokens as token_name:token 
    Returns None 
    """

    if not tokens: 
        raise Exception('Invalid params.')

    with open(os.path.join(spotify_dir, 'spotify-tokens.json'), 'w') as tokens_file: 
        tokens_file.write(json.dumps(tokens, indent=4))
        
@decorators.main_logger(module_name)
def refresh_token(): 
    """
    Refreshes user authentication token if appropriate auth token exists 
    No params 
    Returns True if successful else None 
    """

    _, refresh_token = get_tokens() 

    grant_type = 'refresh_token' 

    endpoint = 'https://accounts.spotify.com/api/token'

    client_id, client_secret = api_help.get_auth() 
    
    data = {
        'grant_type': grant_type, 
        'refresh_token': refresh_token, 
        'client_id': client_id, 
        'client_secret': client_secret, 
    }

    response = api_help.requests_general('post', endpoint, data)

    access_token = response['access_token']

    tokens = {
        'access_token': access_token, 
        'refresh_token': refresh_token, 
    }

    post_tokens(tokens)

    return True 

if __name__ == '__main__': 
    # print(get_tokens())
    refresh_token()
    # print(api_help.get_auth())