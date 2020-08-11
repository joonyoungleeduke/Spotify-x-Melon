import logging
import os 
import json 
import requests 
import sys 

base_dir = os.path.dirname(os.path.abspath(__file__))
info_dir = os.path.join(base_dir, 'info')
text_dir = os.path.join(info_dir, 'texts')

from start import spotify_setup
from main import playlist, spotify_run, melon_data
from helpers import others_help, tokens_help, decorators
from logs import loggers

# LOGGERS 
logger = loggers.create_main_logger('main_logger')
d_logger = loggers.create_alert_logger('display_logger')

def test(): 

    with open(os.path.join(info_dir, 'TESTING.json'), 'w'): 
        pass 

    with open(os.path.join(info_dir, 'TESTING.json')) as f: 
        content = json.loads(f.read()) 

    print(content)

    return True 

@decorators.main_logger('manage.py')
def main(sys_args): 
    """
    Handles main terminal args with manage.py given by user 
    Takes in terminal args as params 
    Returns None 
    """

    cmds = {
        '-h': ('file', 'help.txt'), 
        'auth-setup': ('function', spotify_setup.main), 
        'quick-setup': ('function', playlist.main_both),
        'refresh': ('function', spotify_run.refresh),
        'show-tops': ('function', melon_data.show_tops),
        'clear-preferences': ('function', playlist.clear_preferences),
        'get-songs': ('function', melon_data.main_create),
        'create-playlists': ('function', playlist.main_create), 
        'populate-playlists': ('function', playlist.put_playlists), 
        'refresh-token': ('function', tokens_help.refresh_token),
        'clear-logs': ('function', others_help.clear_logs),
        'test': ('function', test),
    }

    if len(sys_args) == 1: 
        arg = '' 
    else: 
        arg = sys_args[1] 
    
    if cmds.get(arg, None) is None:
        with open(os.path.join(text_dir, 'default.txt')) as f:  
            others_help.print_contents(f.read())
        return 

    cmd, cmd_item = cmds.get(arg)

    if cmd == 'file': 
        if not os.path.exists(os.path.join(text_dir, cmd_item)): 
            raise Exception('Error in cmds repository of main() -- cmd item not found.')

        with open(os.path.join(text_dir, cmd_item)) as f: 
            others_help.print_contents(f.read()) 

        return 

    elif cmd == 'function': 

        if cmd_item(): 
            print(f'FULLY RAN COMMAND {arg}.')
        else: 
            print(f'PROCESS ERROR RUNNING COMMAND {arg}')

        return 

    else: 
        raise Exception('Error in cmds repository of main() -- cmd not found.')

if __name__ == '__main__': 
    main(list(sys.argv))