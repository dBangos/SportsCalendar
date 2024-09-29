# Script that scraps itnwwe.com for UFC match dates and times
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup as bs

def ufc():
    # Loading the data
    page = "https://www.espn.com/mma/schedule"
    headers = {'User-Agent':
                   'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
    pageTree = requests.get(page, headers=headers)
    soup = bs(pageTree.content, 'html.parser')

    # Getting the data table ==========================================
    tables = soup.find_all("tbody", {"class": "Table__TBODY"})[:2]
    data = []
    for table in tables:
        table_rows = table.find_all('tr')
        for row in table_rows:
            columns = row.find_all('td')
            data.append([ele.text.strip() for ele in columns])

    # Extracting the event names ===============================================
    matches = []
    for i in data:
        matches.append(i[3])
    # Extracting the event time and date =========================================
    dates = []
    for i in data:
        dates.append(i[0]+" "+i[1])
    # Merging data into final output ======================================
    result = []
    for i in range(len(data)):
        try:  # Fixes the case where events with date but no time set get through
            final_date = datetime.strptime(dates[i], "%b %d %I:%M %p")
        except:
            break
        final_date = final_date.replace(year=2024)
        result.append([matches[i], final_date, "/static/icons/mma_logo.png"])

    for item in result:
        timezone_aware = item[1].replace(tzinfo=ZoneInfo("US/Eastern"))  # EPSN uses est time
        item[1] = timezone_aware.astimezone(ZoneInfo('Europe/Athens'))  # It seems this is an hour too late so I changed it
    return result
