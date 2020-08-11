import os 
import sys 
import requests
import json 
import pprint
from bs4 import BeautifulSoup 
import logging 

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
info_dir = os.path.join(base_dir, 'info')
melon_dir = os.path.join(info_dir, 'melon_data')
spotify_dir = os.path.join(info_dir, 'spotify_data')
sys.path.append(base_dir) 

from helpers import others_help, decorators

logger = logging.getLogger('main_logger')
d_logger = logging.getLogger('display_logger')

module_name = 'melon_data.py'

@decorators.main_logger(module_name)
def get_categories(): 
    """
    Gives valid Melon chart categories 
    No params 
    Returns a dict with category:url str keys 
    """

    return {
        'hits': 'https://www.melon.com/chart/index.htm',
        'day': 'https://www.melon.com/chart/day/index.htm',
        'week': 'https://www.melon.com/chart/week/index.htm',
        'month': 'https://www.melon.com/chart/month/index.htm',
    }

@decorators.main_logger(module_name)
def create_tops(period): 
    """
    Parses 'Melon''s top songs charts for the top songs in South Korea, creates files 
    Accepts string param, only of 'hits', 'day', 'week', 'month' 
    Returns None
    """

    periods = get_categories() 

    print(f'create_tops(): Beginning top songs charts creation for {period} period(s)...')

    if not periods.get(period, None): 
        print("Error. Invalid period, must be ('hits', 'day', 'week', 'month')")
        return 

    url = periods.get(period, None) 
    headers = {
        'User-Agent': 'test',
        'Content-type': 'text/html',
    }

    response = requests.get(url, headers=headers) # APART FROM REQUESTS_GENERAL BECAUSE USES response.text -- this is used only once

    if response.status_code == 200: 
        soup = BeautifulSoup(response.text, 'lxml')
        all_info = soup

        response = {}

        try: 
            table = all_info.find('table')

            for row in table.find_all('tr'): 
                try: 
                    title = row.find('div', class_='rank01')
                    title = title.span.a.text 
                    author = row.find('div', class_='rank02')
                    author = author.a.text
                    response[title] = author 
                except: 
                    pass 
            
            if others_help.file_contents(melon_dir, f'{period}.json', data=response) is None: 
                raise Exception(f'Error writing contents to {period}.json.')
            
            print(f'create_tops(): Added data for {period} period(s)...')

        except: 
            print('Error during initial parsing.')
            return 
    else: 
        print(f"Response Error: {response.status_code}")
        return 

@decorators.main_logger(module_name)
def get_tops(select=None):
    """
    Gets top items for all or select Melon chart category top songs 
    Accepts an optional array of select charts, default is every chart 
    Returns None
    """ 

    if select: 
        if not isinstance(select, list): 
            raise Exception('get_tops(): optional param must be an array/list.')
    else: 
        select = get_categories()
    
    categories = get_categories()
    response = {} 

    for chart in select: 
        if not categories.get(chart, None): 
            raise Exception(f'get_tops(): List item "{chart}" is invalid, must be "hits", "day", "week", or "month".')

        charts = others_help.file_contents(melon_dir, f'{chart}.json')

        response[chart] = charts 

    return response 

@decorators.main_logger(module_name)
def show_tops(): 
    """
    Shows top songs in list selected by user 
    No params 
    Returns True if successful else None 
    """

    select = str(input('Enter one of "hits", "day", "week", or "month": '))

    categories = get_categories() 
    if not select: 
        raise Exception('show_tops(): select is a required parameter that must be "hits", "day", "week", or "month"')
    if not categories.get(select, None): 
        raise Exception('show_tops(): select must be "hits", "day", "week", or "month"')
    
    chart = get_tops([select])

    pprint.pprint(chart)

    return True 

@decorators.main_logger(module_name)
def main_create(select=None): 
    """
    Handles creation of top songs lists 
    Accepts optional array of chart names 
    Returns True if successful else None  
    """
    
    if not select: 
        select = get_categories() 

    for chart in select:
        create_tops(chart)

    return True 

if __name__ == "__main__":
    # for period in periods: 
    #     get_tops(period)
    # import pprint 

    # # pprint.pprint(get_tops())
    # pprint.pprint(get_tops(['month']))
    main_create()