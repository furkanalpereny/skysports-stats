from bs4 import BeautifulSoup
import requests
import json
import pprint

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

def get_seasons():
    link = mainLink + "/premier-league-results"
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
        satir = i.find_all('a', href=True)
        link = satir[0]['href']
        link = push_stats(link)
        matches.append(link)
    
    #son 180
    gelenVeri = gelenVeri[0].find_all('script', attrs={'type': 'text/show-more'})[0].text
    gelenVeri = BeautifulSoup(gelenVeri, "html.parser")
    gelenVeri = gelenVeri.find_all('div', attrs={'class': 'fixres__item'})
    
    for i in gelenVeri:
        satir = i.find_all('a', href=True)
        link = satir[0]['href']
        link = push_stats(link)
        matches.append(link)

    return matches

def make_column_name(name):
    name = name.rstrip()
    name = name.lower()
    name = name.replace(' ','_')
    return name

def get_stats(link):
    _dict = {}
    hamVeri = soup(link)

    #MATCH DETAILS
    match_details = hamVeri.find_all("div",attrs={"class":"match-head__fixture-side match-head__fixture-side--wide-score"})

    for idx, item in enumerate(match_details):
        team_name = item.find_all("abbr",attrs={"class":"swap-text--bp10"})[0]["title"]
        team_score = item.find_all("span",attrs={"class":"match-head__score"})[0].text
        team_score = team_score.strip()
        if idx == 0:
            _dict["team_name_home"] = team_name
            _dict["team_score_home"] = team_score
        if idx == 1:
            _dict["team_away"] = team_name
            _dict["team_score_away"] = team_score

    #STATISTICS
    match_stats = hamVeri.find_all("div",attrs={"class":"match-stats callfn"})
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

def write_json(season):
    print("Getting matches...")
    matches = get_matches(season)
    stats = []

    for idx, item in enumerate(matches):
        stats.append(get_stats(item))
        print("{0}/{1} => {2}".format(idx,len(matches),item))
    
    season = season.replace('/','_')
    json_name = season+'.json'
    print("Creating {0}".format(season))
    with open(json_name, 'w') as outfile:
            json.dump(stats, outfile)

def main():
    print("Welcome to SkySports Puller v1.0.0")
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

    sleagues[int(index)])

    # print("Hello, World!")
    # seasons = get_seasons()
    # for i in range(0,9):
    #write_json("/premier-league-results/2018-19")
        
    
if __name__ == '__main__':
    main()
