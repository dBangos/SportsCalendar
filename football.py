# Script that scraps transfermarkt for football match dates and times
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup as bs


def football(page):
    # Parsing the URL ========================================================
    url = page.split("/")
    if url[2] != 'www.transfermarkt.com':  # If the site is wrong return empty lists to be ignored
        return [], []
    else:
        while len(url) < 11:  # Making sure the URL has the correct size
            url.append("")
        url[4] = 'spielplan'  # Replacing parts of the url to match the required one
        url[7] = 'saison_id'
        url[8] = '2024'
        url[9] = 'plus'
        url[10] = '1'
        final_url = ("/".join(url))

    # Loading the data========================================================
    headers = {'User-Agent':
                   'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
    pageTree = requests.get(final_url, headers=headers)
    soup = bs(pageTree.content, 'html.parser')

    match_strings = soup.find_all("td", {"class": "zentriert no-border-rechts"})
    # Checking if the year is right ============================================
    while len(match_strings) < 2:  # If the URL is of the wrong year, go a year back
        url = final_url.split("/")
        url[8] = str(int(url[8]) - 1)
        final_url = ("/".join(url))
        headers = {'User-Agent':
                   'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
        pageTree = requests.get(final_url, headers=headers)
        soup = bs(pageTree.content, 'html.parser')
        match_strings = soup.find_all("td", {"class": "zentriert no-border-rechts"})

    # Extracting the team's title ============================================
    title = [s for div in soup.find_all("h1", {"class": "data-header__headline-wrapper"}) for s in div.stripped_strings]

    # Extracting the team names ===============================================
    temp = []
    temp_img = []
    for i in match_strings:  # temp contains all the names  temp_img contains all the image sources
        temp.append(i.find('img')["alt"])
        temp_img.append(i.find('img')["data-src"])
    # Extracting the match date and time ======================================
    a = [s for div in soup.select('.zentriert') for s in div.stripped_strings]
    date_time = []
    day_list = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    time_list = ['PM', 'AM']
    for item in a:
        if any(substring in item for substring in day_list):  # If the string is a date
            date_time.append(item)
        elif any(substring in item for substring in time_list):  # If the string is a timestamp
            date_time.append(item)
        elif item == 'Unknown':  # If unknown still include to not mess up the order
            date_time.append(item)

    # Merging data into final output ======================================
    matches = []
    for i in range(int(len(temp)/2)):  # Turn the names into matches by putting them side by side
        # Convert the string to date time before returning it
        if date_time[2*i] != "Unknown" and date_time[2*i+1] != "Unknown":
            final_date = datetime.strptime(date_time[2*i] + " " + date_time[2*i+1], "%a %b %d, %Y %I:%M %p")
            matches.append([temp[2*i] + " - " + temp[2*i+1], final_date, temp_img[2 * i], temp_img[2 * i + 1]])
    # Adjusting the timezone ============================================
    for item in matches:
        timezone_aware = item[1].replace(tzinfo=ZoneInfo("Europe/Berlin"))  # Transfermakrt uses Berlin time
        item[1] = timezone_aware.astimezone(ZoneInfo('Europe/Athens'))

    return matches, title
