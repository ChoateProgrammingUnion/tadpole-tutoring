from browser import document, alert
import browser
from browser.template import Template
import urllib.request
import urllib.parse
import pickle
import base64
import datetime
import collections
import javascript


def toggle_bind(event):
    """
    Binds to the toggle and figures out what to do
    """
    value = bool(document['switch-tutor-value'].text.rstrip())

    if not value:
        tutor_html = fetch_template("tutor_template.html")
        document['results'].html = tutor_html
        document['switch-tutor-value'].text = "True"

        search_by_tutor()

    else:
        time_html = fetch_template("time_template.html")
        document['results'].html = time_html
        document['switch-tutor-value'].text = ""

        search_by_time()


def search_by_time(): 
    """
    searches by time
    """
    time_html = fetch_template("time_template.html")

    document['results'].html = time_html

    times = fetch_api("/api/search-times", params={"tz_offset": calculate_timezone_offset()})
    timeslots = generate_calendar_html(times)

    document['schedule-results'].html = timeslots

    # document['schedule-results'].html = tutor_bio_html

def generate_calendar_html(times):
    """
    Generates calendar table html code given a list of times
    """
    timeslot_html = fetch_template("timeslots_template.html")
    timeslots_days_html = fetch_template("timeslots_days_template.html")
    print("Times api", times, calculate_timezone_offset())

    timeslots = ""
    timeslots += timeslots_days_html
    ids_list = []
    for each_day in times.values():
        timeslots += "<tr>"
        for each_session in each_day:
            # timeslots += timeslot_html.format(id=i, time="None")
            ids_list.append(each_session.get('id'))
            print("Each session", each_session)
            timeslots += timeslot_html.format(**each_session)
        timeslots += "</tr>"

    print(ids_list)
    return timeslots

def search_by_tutor():
    response_dict = fetch_teachers()
    total_count, tutor_bio_html = render_tutor_bios(response_dict)
    print("Tutor HTML", tutor_bio_html)

    # set and save
    document['schedule-results'].html = tutor_bio_html
    for i in range(total_count):
        try:
            document[str(i)].bind("mousedown", render_tutor)
            # document["clicky-slider"] = ""

        except KeyError as e:
            print("Error, need to debug later", e)


def render_tutor(ev=""):
    # print(ev, dir(ev))
    # print("EV target", str(list(ev.target)), ev.target.get(), ev.target.id)
    # print(dir(ev.target))
    print("ev.target.id", ev.target.id)

    # print("repr", repr(ev.target))

    index = int(ev.target.id)

    tutor_dict = fetch_teachers()[index]
    print("Tutor dict", tutor_dict)

    indiv_tutor_template = fetch_template("indiv_tutor_template.html").format(**tutor_dict)
    document['results'].html = indiv_tutor_template

    schedule_now()

    document['schedule-' + tutor_dict['id']].bind("mousedown", schedule_now)

    # cart_html = fetch_template("tutor_template.html")
    # document['results'].html = cart_html

def schedule_now():
    email = document['email'].html.rstrip()
    print("email", email)
    response = fetch_api("/api/search-times",{'teacher_email': email})

    print("API Teacher Response", response)

    if response:
        calendar_template = generate_calendar_html(response)
        document['schedule-results'].html = calendar_template


def render_tutor_bios(vars):
    """
    Fetches and renders template
    """
    # URL = str(browser.window.location.href).replace(str(browser.window.location.pathname), "/")
    response = fetch_template("/teacher_bio.html")
    html = ""
    for count, each_var in enumerate(vars):
        each_var["id"] = str(count)
        print(response, each_var)
        html += response.format(**each_var)

    return len(vars), html


## Fetching code

def fetch_template(url):
    """
    Fetches and renders template
    """
    response = urllib.request.urlopen(url).read().rstrip()
    return response

def fetch_api(endpoint="/api/search-times", params={}):
    """
    Fetches stuff from any API endpoint
    """
    URL = "http://localhost:5000"
    # URL = "http://api.tadpoletutoring.org"
    if "teacher_email" in params:
        response_raw = urllib.request.urlopen(URL + endpoint+"?teacher_email=" + params.get("teacher_email")).read().rstrip()
    else:
        response_raw = urllib.request.urlopen(URL + endpoint).read().rstrip()

    response_decode = base64.b64decode(response_raw.encode())
    response = pickle.loads(response_decode)
    return response

def fetch_teachers():
    """
    Fetches teacher from /api/teachers
    """
    # URL = "http://localhost:5000"
    # response = urllib.request.urlopen(URL + "/api/teachers").read().rstrip()
    # response_decode = base64.b64decode(response.encode())
    # response_dict = pickle.loads(response_decode)
    response_dict = fetch_api("/api/teachers")

    filtered_dict = []
    for count, each_var in enumerate(response_dict):
        filtered_dict.append({x_var: y_var for _, (x_var, y_var) in each_var.items()})

    return filtered_dict

def calculate_timezone_offset():
    date = javascript.Date.new()
    return int(date.getTimezoneOffset())

document["switch-tutor"].bind("mousedown", toggle_bind)
search_by_time()
