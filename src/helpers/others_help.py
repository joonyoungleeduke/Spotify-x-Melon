import os 
import json 
import logging 
import readline

logger = logging.getLogger('main_logger')
d_logger = logging.getLogger('display_logger')

from . import decorators, colors

module_name = 'others_help.py'

def alert_error(): 
    """
    Simple helper to display error with logger 
    No params 
    No return 
    """

    d_logger.info('EXCEPTION: Check "logs" for detailed view')

    return 

def print_contents(content): 
    """
    Simple helper function to print out content with spaces for visibility 
    No params 
    Returns None 
    """

    print(4*'\n')
    print(content) 
    print(4*'\n')

    return 

def print_error(msg): 
    """
    Prints errors in appropriate color format 
    """
    print(colors.Colors.bold + colors.Colors.lightred + msg + colors.Colors.lightred + colors.Colors.bold + colors.Colors.reset)

def print_alert(msg): 
    """
    Prints alerts in appropriate color format 
    """
    print(colors.Colors.bold + msg + colors.Colors.bold + colors.Colors.reset)

def prefill_input(prompt, prefill): 
    """
    Prefills input 
    No params 
    Returns user response 
    """
    def hook(): 
        readline.insert_text(prefill) 
        readline.redisplay() 
    readline.set_pre_input_hook(hook)
    response = input(prompt) 
    readline.set_pre_input_hook() 
    return response 

@decorators.main_logger(module_name)
def clear_logs(): 
    """
    Clear logs 
    No params 
    Returns True if successful else None  
    """

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if not os.path.exists(os.path.join(base_dir, 'logs')): 
        raise Exception('"logs" directory does not exist.')
    logs_dir = os.path.join(base_dir, 'logs')

    request = str(input('"all" to clear all logs or write space separated names of the logs (actions, errors, requests): '))

    choices = request.split() if request else 'none'

    options = {
        'all': ['actions', 'errors', 'requests'], 
        'actions': ['actions'], 
        'errors': ['errors'], 
        'requests': ['requests'], 
    }

    for choice in choices: 
        files = options.get(choice, None) 

        if not files: 
            raise Exception('Invalid input.')
        
        for log in files: 
            with open(os.path.join(logs_dir, f'{log}.log'), 'w'): 
                pass 
    
    return True 

@decorators.main_logger(module_name)
def file_contents(dir_path, name, data=None):
    """
    Handles files for writing or reading 
    Accepts required params of dir path, name, optional params of data and write (default False) 
    Returns contents or True if contents or written else None 
    """ 

    if data is None and not os.path.exists(os.path.join(dir_path, name)):  # reading but file does not exist 
        raise Exception(f'File {name} does not exist.')
    
    action = 'w' if data is not None else 'r' 

    with open(os.path.join(dir_path, name), action) as f: 
        if data is not None: 
            f.write(json.dumps(data, indent=4))
            return True 
        else: 
            try: 
                content = json.loads(f.read())
            except: 
                content = None 
            return content 

@decorators.main_logger(module_name)
def validate_choices(choices, msg=None): 
    """
    Presents choices to user and validates them -- ONLY WORKS WITH SINGULAR CHOICES 
    Accepts required param of ARRAY choices, optional param of msg 
    Returns choice if valid else None 
    """

    if not isinstance(choices, list) or len(choices) == 0: 
        raise Exception('Required param "choices" must be a list of at least length 1.')
    
    options = {} 
    
    for choice in choices: 
        options[choice] = 1

    if msg is None: 
        # msg = ' or '.join(choices) -- did not do this because does not provide quotes around choices 
        msg = f'"{choices[0]}" '
        for choice in choices[1:]: 
            msg += f'or "{choice}" '

    while True: 
    
        response = str(input(msg))

        if options.get(response, None) is None: 
            print_error('Invalid choice.') # can do return ... (one liner) but would not get this msg
        else: 
            break 
    
    return response 