import requests
from bs4 import BeautifulSoup
from datetime import datetime
from get_athlete_data import get_athlete_races
import time
import pandas as pd

# get_team_data
#
# Purpose: create a profile for the team to feed to ML model: all the athletes are features, and each athlete has
#   a set of races
def get_team_data(school_name, link, year=0):

    link = 'https://www.tfrrs.org/teams/xc/MO_college_m_Washington_U.html'
    page = BeautifulSoup(requests.get(link).content, 'html.parser').find('select', class_="form-control")

    season_name = str(year) + 'CrossCountry'
    seasons = page.find_all('option')

    val = -1
    for season in seasons:
        if season.text.replace(' ','').replace('\n', '') == season_name:
            val = season.get('value')
            break

    if int(val) < 0:
        raise ValueError(year, " XC season not found. Check that year is valid")
    
    link = link + '?config_hnd=' + val #navigate dropdown to specific xc season
    page = BeautifulSoup(requests.get(link).content, 'html.parser')
    
    page = page.find('tbody')
    roster = page.find_all('tr')

    data = []
    for athlete in roster:
        
        athlete = athlete.find('a')
        athlete_name = athlete.text.replace('\n','').replace(' ','')
        races = get_athlete_races(('https://www.tfrrs.org' + athlete.get('href')), year)
        if not races is None: 
            for race in races: data.append([school_name, athlete_name] + race)

    return data
    
# goal -- bunch of rows: school name, Athlete, date, time info
#   note: shouldn't include nationals races, as we won't have this info pre-nats

if __name__=='__main__':
    start_time = time.time()
    result = get_team_data('WashU', 'https://www.tfrrs.org/teams/xc/MO_college_m_Washington_U.html', 2022) #running this for washu takes about 10 seconds
    print('time elapsed -- ', time.time() - start_time)

    data = pd.DataFrame(result)
    print(data.head())