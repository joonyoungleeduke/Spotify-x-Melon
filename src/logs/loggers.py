import os
import logging

def create_main_logger(name): 
    """
    Simple helper to create the main logger for the entire program 
    Accepts only name param 
    Returns None 
    """

    logger = logging.getLogger(name)

    # Files and Directory Set Up 
    log_names = ['actions', 'errors']
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if not os.path.exists(os.path.join(base_dir, 'logs')): 
        os.mkdir(os.path.join(base_dir, 'logs'))
    log_dir = os.path.join(base_dir, 'logs')

    files = {}

    for log_name in log_names: 
        if not os.path.exists(os.path.join(log_dir, f'{log_name}.log')): 
            with open(os.path.join(log_dir, f'{log_name}.log'), 'x'): 
                pass 
        files[log_name] = os.path.join(log_dir, f'{log_name}.log')

    # Handler Initial Set Up 
    # display_handler = logging.StreamHandler() 
    info_handler = logging.FileHandler(files.get('actions'))
    errors_handler = logging.FileHandler(files.get('errors'))

    # Handlers with Levels 
    handlers = [(info_handler, logging.INFO),
                (errors_handler, logging.ERROR)]
                # (display_handler, logging.INFO),

    # Filter 
    class customFilter(logging.Filter): 
        def __init__(self, level): 
            self._level = level 

        def filter(self, record): 
            return record.levelno <= self._level 
    
    general_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Levels, Filters, Formatters + Handlers to logger
    for handler, level in handlers: 
        handler.setLevel(level) 
        handler.addFilter(customFilter(level))
        handler.setFormatter(general_format) 
        logger.addHandler(handler)
    
    logger.setLevel(logging.DEBUG)

    return logger 

def create_alert_logger(name): 
    """
    Simple helper to create console ERROR alert logger
    Accepts only name param 
    Returns None 
    """
    logger = logging.getLogger(name) 

    general_format = logging.Formatter('%(asctime)s -- %(message)s')

    display_handler = logging.StreamHandler()
    display_handler.setLevel(logging.INFO) 
    display_handler.setFormatter(general_format)

    logger.addHandler(display_handler) 

    logger.setLevel(logging.INFO) 

    return logger 