from browser import document, alert
import browser
from browser.template import Template
import urllib.request
import pickle
import base64
import collections


def echo(ev):
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

def fetch_template(url):
    """
    Fetches and renders template
    """
    response = urllib.request.urlopen(url).read().rstrip()
    return response

def fetch_template_tutor_bio(vars):
    """
    Fetches and renders template
    """
    # URL = str(browser.window.location.href).replace(str(browser.window.location.pathname), "/")
    response = urllib.request.urlopen("/teacher_bio.html").read().rstrip()
    html = ""
    for count, each_var in enumerate(vars):
        each_dict = {x_var: y_var for _, (x_var, y_var) in each_var.items()}
        each_dict["id"] = "tutor-bio-" + str(count)
        # each_dict = dict(collections.OrderedDict(each_var))
        # html += Template(response).render(**each_dict)
        print(response, each_dict)
        html += response.format(**each_dict)

    return count, html

def search_by_tutor():
    """
    calls api
    """

    # URL = "api.tadpoletutoring.org"
    URL = "http://localhost:5000"
    response = urllib.request.urlopen(URL + "/api/teachers").read().rstrip()
    response_decode = base64.b64decode(response.encode())
    response_dict = pickle.loads(response_decode)
    count, tutor_bio_html = fetch_template_tutor_bio(response_dict)
    print("Tutor HTML", tutor_bio_html)

    # set and save
    document['schedule-results'].html = tutor_bio_html
    for i in range(count):
        document["tutor-bio-" + str(i)].bind("mouseup", render_tutor)

def search_by_time(): 
    """
    searches by time
    """
    time_html = fetch_template("time_template.html")
    document['results'].html = time_html

def render_tutor(ev=""):
    URL = "http://localhost:5000"

    print(ev, dir(ev))
    print(ev.target)
    index = int(ev.target[-1:])
    response = urllib.request.urlopen(URL + "/api/teachers").read().rstrip()
    response_decode = base64.b64decode(response.encode())
    response_dict = pickle.loads(response_decode)

    print(response_dict[index])
    tutor_dict = {x_var: y_var for _, (x_var, y_var) in response_dict[index].items()}
    print(tutor_dict)

    indiv_tutor_template = fetch_template("indiv_tutor_template.html").format(**tutor_dict)
    document['results'].html = indiv_tutor_template
    # cart_html = fetch_template("tutor_template.html")
    # document['results'].html = cart_html


document["switch-tutor"].bind("mouseup", echo)
# jq = browser.window.jQuery
# jq("#clicky-slider").click()