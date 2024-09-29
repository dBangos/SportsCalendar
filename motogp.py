# Script that scraps autosport.com for MotoGP race dates and times
import zoneinfo

import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup as bs


def motogp():
    # Loading the data
    page = "https://www.autosport.com/motogp/schedule/2024/"
    headers = {'User-Agent':
                   'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
    pageTree = requests.get(page, headers=headers)
    soup = bs(pageTree.content, 'html.parser')
    # Getting the data table ==========================================
    table = soup.find_all('table')
    table_rows = table[0].find_all('tr')
    data = [[] for row in table_rows]
    for row in table_rows:
        columns = row.find_all('td')
        for column in columns:
            for string in column.stripped_strings:
                if string != "-":
                    data[table_rows.index(row)].append(string)

    # Getting the correct times ========================================
    timestamps = soup.find_all('span', {'class': 'ms-schedule-table-date--your'})
    for i in range(len(timestamps)):
        timestamps[i] = timestamps[i]['data-datems']

    # Removing empty values and junk ===================================
    data = data[1:]
    timestamp_offset = 0
    for i in range(len(data)):
        if len(data[i]) == 2 or data[i][2] == 'Postponed':  # Removing cancelled items and adjusting timestamps
            data[i] = ""
            timestamp_offset += 1
        elif len(data[i]) == 3:  # Removing the extra rows/ race titles of the table
            data[i] = ""  # Placeholder for the removal, not to mess up the loop index
        else:
            data[i][0] = "MotoGP " + data[i][0] + " " + data[i][1]
            data[i][1] = datetime.fromtimestamp(int(timestamps[i-timestamp_offset]))
            data[i].pop(2)
            data[i].pop(2)
    data = [i for i in data if i != '']  # Removing the extra rows/ race titles of the table

    # Adjusting the timezone ============================================
    for item in data:
        timezone_aware = item[1].replace(tzinfo=ZoneInfo("GMT-0"))  # This is the server's local time
        item[1] = timezone_aware.astimezone(ZoneInfo('Europe/Athens'))
        item.append("/static/icons/Moto_Gp_logo.png")
    return data
