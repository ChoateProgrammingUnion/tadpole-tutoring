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
    timeslots_days_html = fetch_template("timeslots_days_template.html")
    timeslot_html = fetch_template("timeslots_template.html")

    document['results'].html = time_html

    times = fetch_api("/api/search-times", params={"tz_offset": calculate_timezone_offset()})
    print("Times api", times, calculate_timezone_offset())

    timeslots = ""
    timeslots += timeslots_days_html
    for each_day in times:
        timeslots += "<tr>"
        for each_session in each_day:
            # timeslots += timeslot_html.format(id=i, time="None")
            print(each_session)
            timeslots += timeslot_html.format(**each_session)
        timeslots += "</tr>"

    document['schedule-results'].html = timeslots

    # document['schedule-results'].html = tutor_bio_html


def search_by_tutor():
    response_dict = fetch_teachers()
    tutor_bio_html = render_tutor_bios(response_dict)
    print("Tutor HTML", tutor_bio_html)

    # set and save
    document['schedule-results'].html = tutor_bio_html
    for i in range(0, len(tutor_bio_html) - 1):
        print(i)
        document["tutor-bio-" + str(i)].bind("mousedown", render_tutor)


def render_tutor(ev=""):
    # print(ev, dir(ev))
    # print(ev.target)

    index = int(ev.target[-1:])
    tutor_dict = fetch_teachers()[index]
    print(tutor_dict)

    indiv_tutor_template = fetch_template("indiv_tutor_template.html").format(**tutor_dict)
    document['results'].html = indiv_tutor_template

    # cart_html = fetch_template("tutor_template.html")
    # document['results'].html = cart_html


def render_tutor_bios(vars):
    """
    Fetches and renders template
    """
    # URL = str(browser.window.location.href).replace(str(browser.window.location.pathname), "/")
    response = fetch_template("/teacher_bio.html")
    html = ""
    for count, each_var in enumerate(vars):
        each_var["id"] = "tutor-bio-" + str(count)
        print(response, each_var)
        html += response.format(**each_var)

    return html

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
    # URL = "http://localhost:5000"
    URL = "api.tadpoletutoring.org"
    if params:
        encoded_params = urllib.parse.urlencode(params)
        response_raw = urllib.request.urlopen(URL + endpoint+"?" + encoded_params).read().rstrip()
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
