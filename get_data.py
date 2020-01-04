from bs4 import BeautifulSoup
import requests
import json
import pprint
import os
from datetime import datetime

mainLink = "https://www.skysports.com"

def soup(link):
    r = requests.get(link)
    soup = BeautifulSoup(r.content, "html.parser")
    return soup

def get_leagues():
    leagues = []
    link = "https://www.skysports.com/football/competitions"
    ham_veri = soup(link)
    ul = ham_veri.find_all('ul', attrs={'class': 'category-list__sub-links'})
    for li in ul:
        li = li.find_all('li')
        for li_item in li:
            a = li_item.find_all('a',href=True)
            leagues.append(a[0]['href'])
    return leagues

def get_seasons(league):
    link = mainLink + league +"-results"
    gelenVeri = soup(link) 
    gelenVeri = gelenVeri.find_all('div', attrs={'class': 'section-nav__body'})
    gelenVeri = gelenVeri[0].find_all('ul', attrs={'class': 'section-nav__group'})
    gelenVeri = gelenVeri[0].find_all('li', attrs={'class': 'section-nav__item'})

    seasons = []
    for i in gelenVeri:
        satir = i.find_all('a',href=True)
        seasons.append(satir[0]['href'])

    return seasons

def push_stats(link):
    a = link.split('/')
    a.insert(5,"stats")
    new_link = ""
    for i in a:
        new_link = new_link + i + '/'
    return new_link

def get_matches(season):
    link = mainLink + season
    matches = []
    gelenVeri = soup(link) 
    gelenVeri = gelenVeri.find_all('div', attrs={'class': 'fixres__body'})

    #ilk 200
    ilk200 = gelenVeri[0].find_all('div', attrs={'class': 'fixres__item'})
    for i in ilk200:
        a = i.find_all('a', href=True)
        href = a[0]['href']
        href = push_stats(href)
        matches.append(href)
    
    #son 180
    try:
        script = gelenVeri[0].find_all('script', attrs={'type': 'text/show-more'})[0].text
        script = BeautifulSoup(script, "html.parser")
        script = script.find_all('div', attrs={'class': 'fixres__item'})
        
        for i in script:
            a = i.find_all('a', href=True)
            href = a[0]['href']
            href = push_stats(href)
            matches.append(href)

    except:
        print("Last 180 is not exist...")

    return matches

def make_column_name(name):
    name = name.rstrip()
    name = name.lower()
    name = name.replace(' ','_')
    return name

def get_stats(link):
    _dict = {}
    rawData = soup(link)

    #MATCH DETAILS
    match_details = rawData.find_all("div",attrs={"class":"match-head__fixture-side match-head__fixture-side--wide-score"})

    for idx, item in enumerate(match_details):
        team_name = item.find_all("abbr",attrs={"class":"swap-text--bp10"})[0]["title"]
        team_score = item.find_all("span",attrs={"class":"match-head__score"})[0].text
        team_score = team_score.strip()
        if idx == 0:
            _dict["team_name_home"] = team_name
            _dict["team_score_home"] = team_score
        if idx == 1:
            _dict["team_name_away"] = team_name
            _dict["team_score_away"] = team_score

    #STATISTICS
    match_stats = rawData.find_all("div",attrs={"class":"match-stats callfn"})
    match_stats_item = match_stats[0].find_all("div",attrs={"class":"match-stats__item"})
    for idx, item in enumerate(match_stats_item):
        column_name = item.find_all("h5",attrs={"class":"match-stats__name"})
        column_name = column_name[0].text
        column_name = make_column_name(column_name)  

        stat = item.find_all("span",attrs={"class":"match-stats__bar", "data-role":"match-stat-home"})[0].text

        _dict[str(column_name + "_home")] = stat 

        stat = item.find_all("span",attrs={"class":"match-stats__bar", "data-role":"match-stat-away"})[0].text

        _dict[str(column_name + "_away")] = stat 

    #MATCH RESULT
    if _dict["team_score_home"] > _dict["team_score_away"]:
        _dict["match_result"] = 1
    elif _dict["team_score_home"] < _dict["team_score_away"]:
        _dict["match_result"] = 2
    else:
        _dict["match_result"] = 0


    pprint.sorted = lambda x, key=None: x

    return _dict
    
def write_json(season, league):
    print("Getting matches...")
    matches = get_matches(season)
    stats = []

    seasonPath = season.replace('/','_')
    filePath = "json/" + league.replace('/','') + '/'
    json_name = filePath + seasonPath + '.json'

    if not os.path.exists(filePath): 
        os.makedirs(filePath)
        
    if not os.path.exists(json_name):
        for idx, item in enumerate(matches):
            print("{0}/{1} => {2}".format(idx,len(matches),item))
            try:
                stats.append(get_stats(item))
            except:
                print("Can not pull datas of " + item)
                data = []
                if os.path.exists("logs.json"):
                    with open("logs.json", "r") as jsonFile:
                        data = json.load(jsonFile)
                
                try:
                    err_id = int(data[-1]["id"]) + 1
                except:
                    err_id = 0

                log = {
                    "id": err_id, 
                    "type": "error",
                    "time": str(datetime.now()),
                    "league": league,
                    "season": season,
                    "file": json_name,
                    "link": item
                }
                data.append(log)
                with open("logs.json", "w") as jsonFile:
                    json.dump(data, jsonFile)

        print("Creating {0}".format(seasonPath))
        with open(json_name, 'w') as outfile:
                json.dump(stats, outfile, ensure_ascii=False, indent=4)
    else:
        print("Already exist. Missing " + json_name)
    
def main():
    print("Welcome to SkySports Puller v0.0.1")
    print("Loading leagues, please wait...\n")
    leagues = get_leagues()
    for idx, item in enumerate(leagues):
        print("\t{0}. {1}".format(idx,item))

    index = -1
    while 0 > index or len(leagues)-1 < index:
        try:
            index = int(input("\nEnter index of league: "))
        except ValueError:
            print ("Please enter a numeric value!")

    league = leagues[int(index)]
    seasons = get_seasons(league)

    for i in range(0,9):
        print("Getting matches of " + seasons[i])
        write_json(seasons[i], league)
    
if __name__ == '__main__':
    main()
