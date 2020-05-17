from browser import document, alert, aio
import javascript

URL = "https://api.tadpoletutoring.org"

SUBJECTS = ['English',
            'Elementary School Math',
            'Middle School Math',
            'Geometry',
            'Algebra II',
            'Pre-Calc',
            'BC Calc',
            'Introductory Computer Programming',
            'AP Macroeconomics',
            'AP Microeconomics',
            'High School Chemistry',
            'High School Physics']

tutor_template = """<header>
    <h2>Our Tutors</h2>
    <p>We’re super excited to meet and start working with you! Enjoy browsing our comprehensive community of tutors, mentors, and partners.</p>
</header>
<section id="schedule-results">
</section>
"""

teacher_bio_template = """<aside>
    <center>
        <img alt="Profile Picture" src="{icon}" height="150">
        <h3>{first_name} {last_name}</h3>
    </center>
    <p><b>Studies at: </b>Choate Rosemary Hall</p>
    <p><b>Subjects Teaching: </b>{subjects}</p>
    <p><b>Email: </b><span>{email}</span></p>
    <details>
    <summary>Display Bio</summary>
    <p>{bio}</p>
    </details>
</aside>
"""


def deserialize(obj_str):
    return javascript.JSON.parse(obj_str)


async def search_by_tutor():
    response_dict = await fetch_api("/api/teachers")
    total_count, tutor_bio_html = render_tutor_bios(response_dict)

    if total_count == 0:
        tutor_bio_html = '<h2>All tutors for your chosen subject are booked. <a href="/schedule.html"><i>Back</i></a></h2>'

    document['schedule-results'].html = tutor_bio_html


def render_tutor_bios(vars):
    """
    Fetches and renders template
    """
    html = ""
    for count, each_var in enumerate(vars):
        # each_var["id"] = str(count)
        each_var['subjects'] = each_var['subjects'].replace("|", ", ")

        if not 'icon' in each_var:
            each_var['icon'] = "https://github.com/identicons/jasonlong.png"

        html += teacher_bio_template.format(**each_var)

    return len(vars), html

def get_cookies():
    cookie_list = document.cookie.split('; ')
    cookie_dict = dict()
    for c in cookie_list:
        if c == "":
            continue
        cookie_tuple = c.split('=')
        cookie_dict.update({cookie_tuple[0]: cookie_tuple[1].replace('"', '')})
    return cookie_dict

async def fetch_api(endpoint="/api/search-times", params={}):
    """
    Fetches stuff from any API endpoint
    """
    params.update(get_cookies())

    req = await aio.get(URL + endpoint, data=params)
    response = deserialize(req.data)

    return response

document['results'].html = tutor_template
aio.run(search_by_tutor())