from flask import Flask, render_template, request, session
from football import football
from motogp import motogp
from ufc import ufc
from formula import formula
from wrc import wrc
from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo
import random
app = Flask(__name__)
app.secret_key = "your_key_here"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=730)
checkboxes = ['MotoGP', 'Formula 1', 'WRC', 'MMA']
football_matches = {}
ufc_matches = ufc()
motogp_races = motogp()
formula_races = formula()
wrc_races = wrc()


@app.route("/")
@app.route('/index')
def index():  # Homepage
    global checkboxes
    session.permanent = True
    if 'checkboxes' in session:  # Content in checkboxes
        session['checkboxes'] = session.get('checkboxes')  # Reading and updating session data
    else:
        session['checkboxes'] = checkboxes  # Setting session data
    if 'football_links' in session:  # Links loaded from user
        session['football_links'] = session.get('football_links')
    else:
        session['football_links'] = []
    if 'id' in session:  # Specific user id used to differentiate week pages created
        session['id'] = session.get('id')
    else:
        session['id'] = random.randint(0, 100000)
    if 'matches_to_be_rendered' in session:  # User selections
        session['matches_to_be_rendered'] = session.get('matches_to_be_rendered')
    else:
        session['matches_to_be_rendered'] = []
    if 'timezone' in session:  # Holding the timezone string as chosen by the select form
        session['timezone'] = session.get('timezone')
    else:
        session['timezone'] = "Europe/Athens"
    week = add_events_to_days(create_date_list(0), create_match_list(session['matches_to_be_rendered']), 0)
    return render_template('index.html',
                           week=week,
                           id=session['id'],
                           checked=session['matches_to_be_rendered'],
                           checkboxes=session['checkboxes'])


@app.route("/add_team/", methods=['POST'])
def add_team():  # Add a football team. so it can be selected and rendered
    url = request.form.get('addTeam')
    temp_checkboxes = session['checkboxes']  # Using a temp value to not override the server default value
    temp_links = session['football_links']
    if len(url) > 0:  # If the url isn't empty
        temp_matches = football(url)
        if len(temp_matches[0]) > 0:  # If there are matches found (as a way to check if the link is valid)
            if temp_matches[1][0] not in session['checkboxes']:  # If the team hasn't already been added
                temp_checkboxes.append(temp_matches[1][0])  # Add the title of the team to checkboxes
                football_matches[temp_matches[1][0]] = temp_matches[0]  # Add the team to the football matches to be rendered
                temp_links.append(url)
            session['checkboxes'] = temp_checkboxes  # Add the title of the team to session data
            session['football_links'] = temp_links
    week = add_events_to_days(create_date_list(0), create_match_list(session['matches_to_be_rendered']), 0)
    return render_template('index.html',
                           week=week,
                           id=session['id'],
                           checked=session['matches_to_be_rendered'],
                           checkboxes=session['checkboxes'])


@app.route("/refresh/", methods=['POST'])
def refresh():  # Refresh the selected data server side and display the updated results
    global ufc_matches, motogp_races, formula_races, wrc_races
    temp_list = session['matches_to_be_rendered'][:]
    if 'MotoGP' in temp_list:
        motogp_races = motogp()
        temp_list.remove('MotoGP')
    if 'Formula 1' in temp_list:
        formula_races = formula()
        temp_list.remove('Formula 1')
    if 'WRC' in temp_list:
        wrc_races = wrc()
        temp_list.remove('WRC')
    if 'MMA' in temp_list:
        ufc_matches = ufc()
        temp_list.remove('MMA')

    for i in range(0, len(temp_list)):  # Check the matches for every team
        if temp_list[i] in temp_list:  # If checked, add them to be rendered
            url = session['football_links'][i]
            temp_matches = football(url)
            # Update the server variable
            football_matches[temp_list[i]] = temp_matches[0]
    week = add_events_to_days(create_date_list(0), create_match_list(session['matches_to_be_rendered']), 0)
    return render_template('index.html',
                           week=week,
                           id=session['id'],
                           checked=session['matches_to_be_rendered'],
                           checkboxes=session['checkboxes'])


@app.route('/checkbox_selection/', methods=['POST'])
def checkbox_selection():  # Logic for the checkboxes and update button
    temp_list = []
    for name in session['checkboxes']:  # Passing all the checked boxes to a list to be rendered
        if " " in name:
            temp_name = name.split(" ", 1)[0]
        else:
            temp_name = name
        # Make the check with the temp name so the form.get gets recognized
        # Pass the original name to the list so the spacing stays and the checkbox gets checked
        if request.form.get(temp_name):
            temp_list.append(name)
    session['matches_to_be_rendered'] = temp_list
    week = add_events_to_days(create_date_list(0), create_match_list(session['matches_to_be_rendered']), 0)
    return render_template('index.html',
                           week=week,
                           id=session['id'],
                           checked=session['matches_to_be_rendered'],
                           checkboxes=session['checkboxes'])


@app.route('/reset_checkbox/', methods=['POST'])
def reset_checkbox():  # Logic for the checkboxes and update button
    session['checkboxes'] = checkboxes  # Setting session data
    session['football_links'] = []
    session['matches_to_be_rendered'] = []
    week = add_events_to_days(create_date_list(0), create_match_list(session['matches_to_be_rendered']), 0)
    return render_template('index.html',
                           week=week,
                           id=session['id'],
                           checked=session['matches_to_be_rendered'],
                           checkboxes=session['checkboxes'])


@app.route("/change_timezone/", methods=['POST'])
def change_timezone():
    if request.form.get('timezone_select') is not None:  # If it isn't the placeholder assign the value to the session cookie
        session['timezone'] = request.form.get('timezone_select')
    week = add_events_to_days(create_date_list(0), create_match_list(session['matches_to_be_rendered']), 0)
    return render_template('index.html',
                           week=week,
                           id=session['id'],
                           checked=session['matches_to_be_rendered'],
                           checkboxes=session['checkboxes'])

# So the approach is as follows, the user loads teams, then the next x dates are calculated.
# Dates are made into a list and then events are added next to them
# Each date's events get sorted
# Every 7 days are split into a different page.
# Every next page gets called by the htmx tag


def create_date_list(week_number):  # Creates a list where each row is a date
    current_time_tz_adjusted = datetime.now(tz=ZoneInfo(session['timezone']))
    first_date = date(current_time_tz_adjusted.year, current_time_tz_adjusted.month, current_time_tz_adjusted.day) + timedelta(days=7*week_number)
    days = [(first_date + timedelta(days=i)).strftime(' %A  %d/%m/%Y') for i in range(7)]
    days = [[day] for day in days]
    return days


def create_match_list(matches_to_be_rendered):  # Adds matches to be rendered
    temp_table = []
    temp_list = matches_to_be_rendered[:]
    if 'MotoGP' in matches_to_be_rendered:  # Adds MotoGP to be rendered
        temp_table = temp_table + motogp_races
        temp_list.remove('MotoGP')
    if 'Formula 1' in matches_to_be_rendered:  # Adds MotoGP to be rendered
        temp_table = temp_table + formula_races
        temp_list.remove('Formula 1')
    if 'WRC' in matches_to_be_rendered:  # Adds MotoGP to be rendered
        temp_table = temp_table + wrc_races
        temp_list.remove('WRC')
    if 'UFC' in matches_to_be_rendered:  # Adds MotoGP to be rendered
        temp_table = temp_table + ufc_matches
        temp_list.remove('UFC')
    if 'MMA' in matches_to_be_rendered:  # Adds MotoGP to be rendered
        temp_table = temp_table + ufc_matches
        temp_list.remove('MMA')
    for i in range(0, len(temp_list)):  # Check the matches for every team
        if temp_list[i] in temp_list:  # If checked, add them to be rendered
            if temp_list[i] not in football_matches:  # If the matches haven't already been calculated
                url = session['football_links'][i]
                temp_matches = football(url)
                football_matches[temp_list[i]] = temp_matches[0]  # Add the team to the football matches to be rendered
            temp_table = temp_table + football_matches[temp_list[i]]  # Add the matches to be rendered
    return temp_table


def add_events_to_days(days, events, week_number):  # Matches the events to the corresponding days
    time_now = datetime.now(tz=ZoneInfo(session['timezone']))
    rounded_now = time_now.replace(hour=0, minute=0, second=0, microsecond=0)
    rounded_first = rounded_now + timedelta(days=7*week_number)  # Initial date, offset by x weeks
    for event in events:  # Add events to days
        delta = (event[1].astimezone(ZoneInfo(session['timezone'])).replace(hour=0, minute=0, second=0, microsecond=0) - rounded_first).days
        if 7 > delta >= 0:
            # Passing a copy so the original object value doesn't change
            # when changing the displayed time format
            days[delta].append(event[:])
    for day in days:  # Sort the events for every day
        if len(day) > 1:  # If there are events to be sorted
            # Sorting by the second item in each list, the datetime object
            day[1:] = sorted(day[1:], key=lambda x: x[1])
            previous_value = 0
            for i in range(1, len(day)):  # Change the displayed time format to look prettier
                if previous_value != day[i][0]:  # If the value isn't duplicate
                    previous_value = day[i][0]
                    day[i][1] = day[i][1].astimezone(ZoneInfo(session['timezone'])).strftime('%H:%M')
                else:  # Remove the value to not be rendered
                    day[i] = ""  # Set the item to be empty to delete later, to not change the loop index
                day[:] = list(filter(lambda a: a != "", day))  # Remove duplicates
    return days


@app.route('/week/<id>/<some_week>')
def some_week_page(some_week, id):  # Creates the sites to fill the main scroll page
    week = add_events_to_days(create_date_list(int(some_week)),
                              create_match_list(session['matches_to_be_rendered']),
                              int(some_week))
    # number returns the index of the next page to be loaded
    return render_template('week.html', week=week, number=int(some_week)+1, id=session['id'])
