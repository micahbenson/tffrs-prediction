import requests
from bs4 import BeautifulSoup
from datetime import datetime
#from features import build_features

"""
Get list of a particulat athlete's races. Each race is a list of the
format [event (meters), time (seconds), place (no suffix), day, month, year, meet name]
"""
def get_athlete_races(link, year=0, xc=True, track=False):
    page = BeautifulSoup(requests.get(link).content, 'html.parser').find(id='meet-results')
    if page == None: return

    # tfrrs uses different classes for track & xc results
    results = []
    if xc: results += page.find_all('table', class_='table table-hover xc')
    if track: results += page.find_all('table', class_='table table-hover >') 

    races = []
    for result in results:

        date = result.find('span').text.replace(' ', '').replace('\n', '').replace(u'\xa0', '')
        date = datetime.strptime(date, '%b%d,%Y')
        if not year or date.year == year:

            ls = result.find_all('a')
            meet = ls[0].text
            time = ls[1].text

            ls = result.find_all('td')
            event = ls[0].text
            place = ls[2].text 
            
            #2) Convert distance to meters (NOTE: currently for XC only)
            #   note that there also exist weird distances like '4.17k'
            #   assume that string has the format 'nm' where n is some number and m denotes the metric used
            event = event.replace(' ', '').replace('\n', '').replace(u'\xa0', '')
            metric = event[len(event)-1]
            conversions = {'k' : 1000 , 'M' : 1609.34} #keep result the same if the suffix isn't recognized
            if metric in conversions.keys(): event = float(event.replace(metric, ''))*conversions[metric]

            #3) convert time to seconds (note that DNS/DNF flag is stored here instead, if applicable)
            #   assuming format is mm:ss.d (in constrast, track would include two decimal places)
            time = time.replace(' ', '').replace('\n', '').replace(u'\xa0', '')
            if not (time in ['DNS','DNF']): time = int(time[:2])*60 + int(time[3:5]) + int(time[-1])*0.1

            #4) remove letters from place (assuming letters always occupy last two indices of string)
            place = place.replace(' ', '').replace('\n', '').replace(u'\xa0', '')[:-2]
            if place != '': place = int(place)

            #5) clean up meet name
            meet = meet.replace('\n','').replace(' ','-')

            races.append([event, time, place, date.day, date.month, date.year, meet])
    
    return(races)


#right now, just using this to figure out beatifulsoup
# soon: get-Athlete-marks(athlete, start_time, end_time)
if __name__ == '__main__':
    print(get_athlete_races('https://www.tfrrs.org/athletes/7910441/Washington_U/Will_Houser.html', 2021))
    #get_athlete_races('https://www.tfrrs.org/athletes/8238843/Washington_U/Jillian__Heth.html')