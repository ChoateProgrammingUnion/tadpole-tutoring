from browser import document, alert, aio
import javascript

URL = "http://localhost:5000"

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

subject_card_template = """
"""

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

time_template_for_tutor = """<header>
    <h2>Sessions With {first_name} {last_name}</h2>
</header>
<section>
<table id="schedule-results">
</table>
</section>
"""

timeslots_template = """<td><a href="#" onclick="return false;"><i class="timeslot" id="{id}">{start_time}</i></a></td>"""

back_button_template = """<a href="#" onclick="return false;"><i id="back-button">Schedule Another Appointment</i></a>"""

timeslot_display_template = """
<tr><th><a>Tutoring Session Info</a></th></tr>
<tr><td>
    <i>
        <b>Teacher: </b>{first_name} {last_name} <br>
        <b>Subjects: </b> {subjects} <br>
        <b>Time: </b>{start_time}, {date_str} <br>
        <b>Duration: </b>1hr <br>
        <a href="#" onclick="return false;"><i class="add-to-cart" id="{id}">Add To Cart</i></a>
    </i>
</td></tr>"""

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
    <a><strong class="tutor-link" id="{id}">Schedule Now</strong></a>
</aside>
"""

slider_html = document['clicky-slider'].html

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

def update_view(event):
    """
    Binds to the toggle and figures out what to do
    """

    document['back-button-div'].html = ""
    value = bool(document['switch-tutor-value'].text.rstrip())

    if value:
        document['results'].html = tutor_template

        aio.run(search_by_tutor())

    else:
        document['results'].html = time_template

        aio.run(search_by_time())

def add_to_cart(vars):
    display_id = int(vars.target.id)
    aio.run(fetch_api("/api/add-to-cart", {"time_id": display_id}))
    document[str(display_id)].html = "Added to Cart!"

async def fetch_and_display_timeslot(id):
    time_info = await fetch_api("/api/get-time", {"time_id": id, "tz_offset": calculate_timezone_offset()})
    time_info['subjects'] = time_info['subjects'].replace("|", ", ")
    document['schedule-results'].html = timeslot_display_template.format(**time_info)
    document['back-button-div'].html = back_button_template
    document["back-button"].bind("mousedown", update_view)

    user_cart = await fetch_api("/api/get-cart-numbers")

    if id in user_cart:
        document[str(id)].html = "Added to Cart!"
    else:
        for d in document.select(".add-to-cart"):
            d.bind("click", add_to_cart)

def display_timeslot(vars):
    display_id = int(vars.target.id)
    aio.run(fetch_and_display_timeslot(display_id))


async def search_by_time(id=None):
    """
    searches by time
    """

    subject = document['chosen-subject'].html

    if subject == "" or subject == "All Subjects":
        subject = None

    if id is None:
        params = {"tz_offset": calculate_timezone_offset()}
        document['results'].html = time_template
    else:
        params = {"tz_offset": calculate_timezone_offset(), "teacher_id": id}
        teacher = await fetch_api("/api/get-teacher", {'teacher_id': id})
        document['results'].html = time_template_for_tutor.format(**teacher)

    if subject is not None:
        params.update({"subject": subject})

    times = await fetch_api("/api/search-times", params=params)
    timeslots = generate_calendar_html(times)

    document['schedule-results'].html = timeslots

    for d in document.select(".timeslot"):
        d.bind("click", display_timeslot)

    # document['schedule-results'].html = tutor_bio_html

def generate_calendar_html(times):
    """
    Generates calendar table html code given a list of times
    """
    print("Times api", times, calculate_timezone_offset())

    # timeslots = ""
    # timeslots += timeslots_days_template
    # for each_day in times.values():
    #     timeslots += "<tr>"
    #     for each_session in each_day:
    #         print("Each session", each_session)
    #         timeslots += timeslots_template.format(**each_session)
    #     timeslots += "</tr>"

    timeslots = "<tr>"

    for day_name, time_list in times:
        timeslots += "<th><a>{day}</a></th>".format(day=day_name)

    timeslots += "</tr>"

    max_len = max([len(j) for i, j in times])
    for time_num in range(max_len):
        timeslots += "<tr>"
        for day_num in range(len(times)):
            print(times[day_num])

            if len(times[day_num][1]) > time_num:
                timeslots += timeslots_template.format(**times[day_num][1][time_num])
            else:
                timeslots += "<td></td>"

        timeslots += "</tr>"

    return timeslots

def display_tutor_times(vars):
    id = int(vars.target.id)
    aio.run(search_by_time(id))

    document['back-button-div'].html = back_button_template
    document["back-button"].bind("mousedown", update_view)

async def search_by_tutor():
    response_dict = await fetch_teachers()
    total_count, tutor_bio_html = render_tutor_bios(response_dict)

    document['schedule-results'].html = tutor_bio_html

    for d in document.select(".tutor-link"):
        d.bind("click", display_tutor_times)


async def render_tutor(ev=""):
    print("ev.target.id", ev.target.id)

    index = int(ev.target.id)

    tutor_dict = await fetch_teachers()
    tutor_dict = tutor_dict[index]

    tutor_dict['subjects'] = tutor_dict['subjects'].replace("|", ", ")
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
        # each_var["id"] = str(count)
        each_var['subjects'] = each_var['subjects'].replace("|", ", ")
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

async def fetch_teachers():
    subject = document['chosen-subject'].html

    if subject == "" or subject == "All Subjects":
        response_dict = await fetch_api("/api/teachers")
    else:
        response_dict = await fetch_api("/api/teachers", {"subject": subject})

    return response_dict

def calculate_timezone_offset():
    date = javascript.Date.new()
    return int(date.getTimezoneOffset())

def pick_subject(vars):
    document['chosen-subject'].html = vars.target.id
    document['back-to-subject'].html = """<a href="/schedule.html">Pick Another Subject</a>"""

    document['clicky-slider'].html = slider_html
    document["switch-tutor"].bind("mousedown", toggle_bind)

    aio.run(search_by_time())

def subject_chooser():
    document['clicky-slider'].html = ""

    document['results'].html = """<a href="#" onclick="return false;"><i class="subject-button" id="All Subjects">All Subjects</i></a>&nbsp&nbsp"""

    for s in SUBJECTS:
        document['results'].html += """<a href="#" onclick="return false;"><i class="subject-button" id="{subject}">{subject}</i></a>&nbsp&nbsp""".format(subject=s)

    for d in document.select(".subject-button"):
        d.bind("click", pick_subject)

# document["switch-tutor"].bind("mousedown", toggle_bind)
aio.run(subject_chooser())