from browser import document, alert, aio
import javascript

tutor_template = """<header>
    <h2>Our Tutors</h2>
    <p>Our team of tutors is small and tight-knit. Each tutor here is hand-picked to help ensure that you can learn well.</p>
</header>
<section id="schedule-results">
</section>
"""

time_template = """<header>
    <h2>Search by Time</h2>
    <p>Our team of tutors is small and tight-knit. Each tutor here is hand-picked to help ensure that you can learn well.</p>
</header>
<section>
<table id="schedule-results">
</table>
</section>
"""

timeslots_template = """<td><a id="timeslot-{id}"><i>{start_time}</i></a></td>"""

timeslots_days_template = """<tr>
<th><a>Sunday</a></th>
<th><a>Monday</a></th>
<th><a>Tuesday</a></th>
<th><a>Wednesday</a></th>
<th><a>Thursday</a></th>
<th><a>Friday</a></th>
<th><a>Saturday</a></th>
</tr>"""

indiv_tutor_template = """<header>
    <h2>{first_name} {last_name}</h2>
    <p><b>Studies at: </b>Choate Rosemary Hall</p>
    <p><b>Subjects Teaching: </b>{subjects}</p>
    <p><b>Email: </b><span id="email">{email}</span></p>
    <p>{bio}</p>
</header>
<section>
    <table id="schedule-results">
    </table>
</section>"""

teacher_bio_template = """<aside>
    <center>
        <img alt="Profile Picture" src="https://github.com/identicons/jasonlong.png" height="150">
        <h3>{first_name} {last_name}</h3>
    </center>
    <p><b>Studies at: </b>Choate Rosemary Hall</p>
    <p><b>Subjects Teaching: </b>{subjects}</p>
    <p><b>Email: </b><span>{email}</span></p>
    <p>{bio}</p>
    <a><strong id="{id}">Schedule Now</strong></a>
</aside>
"""

def deserialize(obj_str):
    return javascript.JSON.parse(obj_str)

def toggle_bind(event):
    """
    Binds to the toggle and figures out what to do
    """
    value = bool(document['switch-tutor-value'].text.rstrip())

    if not value:
        document['results'].html = tutor_template
        document['switch-tutor-value'].text = "True"

        aio.run(search_by_tutor())

    else:
        document['results'].html = time_template
        document['switch-tutor-value'].text = ""

        aio.run(search_by_time())


async def search_by_time():
    """
    searches by time
    """
    document['results'].html = time_template

    times = await fetch_api("/api/search-times", params={"tz_offset": calculate_timezone_offset()})
    timeslots = generate_calendar_html(times)

    document['schedule-results'].html = timeslots

    # document['schedule-results'].html = tutor_bio_html

def generate_calendar_html(times):
    """
    Generates calendar table html code given a list of times
    """
    print("Times api", times, calculate_timezone_offset())

    timeslots = ""
    timeslots += timeslots_days_template
    ids_list = []
    for each_day in times.values():
        timeslots += "<tr>"
        for each_session in each_day:
            ids_list.append(each_session.get('id'))
            print("Each session", each_session)
            timeslots += timeslots_template.format(**each_session)
        timeslots += "</tr>"

    print(ids_list)
    return timeslots

async def search_by_tutor():
    response_dict = await fetch_teachers()
    total_count, tutor_bio_html = render_tutor_bios(response_dict)
    print("Tutor HTML", tutor_bio_html)

    document['schedule-results'].html = tutor_bio_html
    for i in range(total_count):
        try:
            document[str(i)].bind("mousedown", render_tutor)

        except KeyError as e:
            print("Error, need to debug later", e)


async def render_tutor(ev=""):
    print("ev.target.id", ev.target.id)

    index = int(ev.target.id)

    tutor_dict = await fetch_teachers()
    tutor_dict = tutor_dict[index]
    print("Tutor dict", tutor_dict)

    document['results'].html = indiv_tutor_template.format(**tutor_dict)

    await schedule_now()

    document['schedule-' + tutor_dict['id']].bind("mousedown", schedule_now)

async def schedule_now():
    email = document['email'].html.rstrip()
    print("email", email)
    response = await fetch_api("/api/search-times",{'teacher_email': email})

    print("API Teacher Response", response)

    if response:
        calendar_template = generate_calendar_html(response)
        document['schedule-results'].html = calendar_template


def render_tutor_bios(vars):
    """
    Fetches and renders template
    """
    html = ""
    for count, each_var in enumerate(vars):
        each_var["id"] = str(count)
        print(teacher_bio_template, each_var)
        html += teacher_bio_template.format(**each_var)

    return len(vars), html

async def fetch_api(endpoint="/api/search-times", params={}):
    """
    Fetches stuff from any API endpoint
    """
    # URL = "http://localhost:5000"
    URL = "https://api.tadpoletutoring.org"

    req = await aio.post(URL + endpoint, data=params)
    response = deserialize(req.data)

    return response

async def fetch_teachers():
    response_dict = await fetch_api("/api/teachers")
    return response_dict

def calculate_timezone_offset():
    date = javascript.Date.new()
    return int(date.getTimezoneOffset())

document["switch-tutor"].bind("mousedown", toggle_bind)
aio.run(search_by_time())
