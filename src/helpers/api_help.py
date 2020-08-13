import os 
import json 
import sys 
import requests 
import logging 

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
info_dir = os.path.join(base_dir, 'info')
spotify_dir = os.path.join(info_dir, 'spotify_data')
sys.path.append(base_dir) 

from helpers import others_help, tokens_help, decorators 

logger = logging.getLogger('main_logger')

module_name = 'api_help.py'

@decorators.main_logger(module_name)
def requests_general(form_type, endpoint, data=None, headers=None): 
    """
    General API requests 
    Accepts string params of form_type, endpoint, dic params of data, headers 
    Returns response if successful else None 
    """

    success_codes = {
        200: True, 
        201: True,
    }

    form_types = {
        'get': requests.get,
        'post': requests.post,
        'put': requests.put,
    }

    request = form_types.get(form_type, None)

    if not request: 
        raise Exception('Invalid form type.')

    response = request(endpoint, data=data, headers=headers)
    
    if not success_codes.get(response.status_code): 
        raise Exception(f'Response Error: {response.status_code}\nHeaders: {response.headers}\nContent: {response.content}')

    response = (response.status_code if form_type=='put' else json.loads(response.content))

    return response 

@decorators.main_logger(module_name)
def get_auth(): 
    """
    Get auth creds -- primarily for error checking 
    No params 
    Returns creds if successful else None 
    """

    # ** FOR CODE RELEASE, SPOTIFY-CLIENT.JSON FILE IS WIPED, CREATE YOUR CREDS @ SPOTIFY DEVELOPER SITE ** 
    if not os.path.exists(os.path.join(spotify_dir, 'spotify-client.json')): 
        raise Exception('No spotify-client.json file.')

    with open(os.path.join(spotify_dir, 'spotify-client.json')) as creds_file: 
        client_info = json.loads(creds_file.read()) #client_secret, client_id  
    client_id = client_info.get('client_id', None) 
    client_secret = client_info.get('client_secret', None) 

    if not client_id or not client_secret: 
        raise Exception("Auth creds error. Check 'spotify-client.json'")

    return (client_id, client_secret)

@decorators.main_logger(module_name)
def auth_post(client_info=None, redirect_uri=None, auth_code=None): 
    """
    Posts for access and refresh tokens 
    Accepts tuple of strings (client_id, client_secret) and string auth_code 
    Returns True if successful else None 
    """    

    if not all([client_info, auth_code, redirect_uri]):
        raise Exception('Invalid params for auth_post()')

    grant_type = 'authorization_code'
    endpoint_post = 'https://accounts.spotify.com/api/token'

    client_id, client_secret = client_info 

    data = {
        'grant_type':grant_type, 
        'code': auth_code, 
        'redirect_uri': redirect_uri, 
        'client_id': client_id, 
        'client_secret': client_secret
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = requests_general('post', endpoint_post, data=data, headers=headers)

    access_token = response['access_token']
    refresh_token = response['refresh_token']
    
    tokens = {
        'access_token': access_token, 
        'refresh_token': refresh_token,
    }

    tokens_help.post_tokens(tokens)
    
    return True 