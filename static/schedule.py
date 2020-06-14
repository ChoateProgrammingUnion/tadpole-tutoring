from browser import document, alert, aio
import javascript

URL = "{URL}"

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
    <p>We’re super excited to meet and start working with you! Enjoy browsing our comprehensive community of tutors, mentors, and partners.</p>
</header>
<section id="schedule-results">
</section>
"""

time_template = """<header>
    <h2>Search by Time</h2>
    <p>We’re super excited to meet and start working with you! Enjoy browsing our comprehensive community of tutors, mentors, and partners.</p>
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

timeslots_template = """<td><a href="#" onclick="return false;"><i class="timeslot" id="{_id}">{start_time}</i></a></td>"""

back_button_template = """<a href="#" onclick="return false;"><i id="back-button">Back</i></a>"""

timeslot_display_template = """
<tr><th><a>Tutoring Session Info</a></th></tr>
<tr><td>
    <i>
        <b>Teacher: </b>{first_name} {last_name} <br>
        <b>Subjects: </b> {subjects} <br>
        <b>Time: </b>{start_time}, {date_str} <br>
        <b>Duration: </b>1hr <br>
        <a href="#" onclick="return false;"><i class="add-to-cart" id="{_id}">Add To Cart</i></a>
    </i>
</td></tr>"""

timeslot_display_template_not_logged_in = """
<tr><th><a>Tutoring Session Info</a></th></tr>
<tr><td>
    <i>
        <b>Teacher: </b>{first_name} {last_name} <br>
        <b>Subjects: </b> {subjects} <br>
        <b>Time: </b>{start_time}, {date_str} <br>
        <b>Duration: </b>1hr <br>
        <a href="#" onclick="window.location.reload()"><i>Log in to Reserve a Session</i></a>
    </i>
</td></tr>"""

timeslot_display_template_already_booked = """
<tr><th><a>Tutoring Session Info</a></th></tr>
<tr><td>
    <i>
        <b>Teacher: </b>{first_name} {last_name} <br>
        <b>Subjects: </b> {subjects} <br>
        <b>Time: </b>{start_time}, {date_str} <br>
        <b>Duration: </b>1hr <br>
        <br>
        This tutor has reached their hour limit for the week. Remove other sessions from your <a href="/cart.html">cart</a> to add this one.
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
        <img alt="Profile Picture" src="{icon}" height="150">
        <h3>{first_name} {last_name}</h3>
    </center>
    <p><b>Email: </b><span><a href="mailto:{email}">{email}</a></span></p>
    <p><span><a style="color: #0a721b;" href="{zoom_id}">Zoom Link</a></span></p>
    <details>
    <summary>Display Bio</summary>
    <p>{bio}</p>
    </details>
    <a href="#" onclick="return false;"><strong class="tutor-link" id="{_id}">Schedule Now</strong></a>
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
        document['results'].html = time_template
        document['switch-tutor-value'].text = "True"

        aio.run(search_by_time())

    else:
        document['results'].html = tutor_template
        document['switch-tutor-value'].text = ""

        aio.run(search_by_tutor())

def update_view(event, back=True):
    """
    Binds to the toggle and figures out what to do
    """
    if back:
        document['back-button-div'].html = "<a href='schedule.html'><i>Back</i></a>"

    value = not bool(document['switch-tutor-value'].text.rstrip())

    if value:
        if back:
            document['results'].html = tutor_template

        aio.run(search_by_tutor())

    else:
        if back:
            document['results'].html = time_template

        aio.run(search_by_time())

def add_to_cart(vars):
    display_id = str(vars.target.id)
    aio.run(fetch_api("/api/add-to-cart", {"time_id": display_id}))
    document[str(display_id)].html = "Added to Cart!"


async def fetch_and_display_timeslot(id, main_screen=True):
    time_info = await fetch_api("/api/get-time", {"time_id": id, "tz_offset": calculate_timezone_offset()})
    time_info['subjects'] = time_info['subjects'].replace("|", ", ")

    if "@" in document.cookie:
        user_cart = await fetch_api("/api/get-cart-numbers")
        teacher_is_available = await fetch_api("/api/is-teacher-available", {"time_id": id})

        if teacher_is_available or id in user_cart:
            document['schedule-results'].html = timeslot_display_template.format(**time_info)

            if id in user_cart:
                document[str(id)].html = "Added to Cart!"
            else:
                for d in document.select(".add-to-cart"):
                    d.bind("click", add_to_cart)
        else:
            document['schedule-results'].html = timeslot_display_template_already_booked.format(**time_info)
    else:
        document['schedule-results'].html = timeslot_display_template_not_logged_in.format(**time_info)

    document['back-button-div'].html = back_button_template
    try:
        document['back-to-subject'].html = ""
    except:
        pass

    if main_screen:
        document["back-button"].bind("mousedown", update_view)
    else:
        document["back-button"].bind("mousedown", back_to_tutor_time)

def display_timeslot(vars):
    display_id = str(vars.target.id)
    aio.run(fetch_and_display_timeslot(display_id))

def display_timeslot_id(vars):
    display_id = str(vars.target.id)
    aio.run(fetch_and_display_timeslot(display_id, False))

def back_to_tutor_time(vars):
    aio.run(search_by_time(document['teacher-id'].html))

    document['back-button-div'].html = back_button_template
    try:
        document['back-to-subject'].html = ""
    except:
        pass
    document["back-button"].bind("mousedown", update_view)

async def search_by_time(id=None, update_view=True):
    """
    searches by time
    """

    if id == "":
        id = None

    if id is None:
        document['teacher-id'].html = ""
    else:
        document['teacher-id'].html = id

    subject = document['chosen-subject'].html

    if subject == "" or subject == "All Subjects":
        subject = None

    if id is None:
        params = {"tz_offset": calculate_timezone_offset()}

        if update_view:
            document['results'].html = time_template
    else:
        params = {"tz_offset": calculate_timezone_offset(), "teacher_id": id}

        if update_view:
            teacher = await fetch_api("/api/get-teacher", {'teacher_id': id})
            document['results'].html = time_template_for_tutor.format(**teacher)

    if subject is not None:
        params.update({"subject": subject})

    params.update({"offset": int(document['offset'].html)})
    times = await fetch_api("/api/search-times", params=params)
    timeslots = generate_calendar_html(times)

    document['schedule-results'].html = timeslots

    document['left-arrow'].bind("click", left_arrow)
    document['right-arrow'].bind("click", right_arrow)
    document['this-week'].bind("click", this_week)

    if id is not None and id != "":
        for d in document.select(".timeslot"):
            d.bind("click", display_timeslot_id)
    else:
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

    if int(document['offset'].html) == 0:
        timeslots = """
        <a style="visibility: hidden" href="#" onclick="return false;" id="left-arrow"><i>&larr;</i></a>
        <a style="margin: 0 auto; visibility: hidden" href="#" onclick="return false;" id="this-week"><i>This Week</i></a>
        <a style="float: right" href="#" onclick="return false;" id="right-arrow"><i>&rarr;</i></a>
        <tr>"""
    else:
        timeslots = """
        <a href="#" onclick="return false;" id="left-arrow"><i>&larr;</i></a>
        <a style="margin: 0 auto;" href="#" onclick="return false;" id="this-week"><i>This Week</i></a>
        <a style="float: right" href="#" onclick="return false;" id="right-arrow"><i>&rarr;</i></a>
        <tr>"""

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
    id = str(vars.target.id)
    aio.run(search_by_time(id))

    document['back-button-div'].html = back_button_template
    try:
        document['back-to-subject'].html = ""
    except:
        pass
    document["back-button"].bind("mousedown", update_view)

async def search_by_tutor():
    response_dict = await fetch_teachers()
    total_count, tutor_bio_html = render_tutor_bios(response_dict)

    if total_count == 0:
        tutor_bio_html = '<h2>All tutors for your chosen subject are booked. <a href="/schedule.html"><i>Back</i></a></h2>'

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

        document['left-arrow'].bind("click", left_arrow)
        document['right-arrow'].bind("click", right_arrow)

def left_arrow(vars):
    document['left-arrow'].html = "<i>Loading...</i>"
    document['offset'].html = max(int(document['offset'].html) - 7, 0)
    aio.run(search_by_time(document['teacher-id'].html, False))

def right_arrow(vars):
    document['right-arrow'].html = "<i>Loading...</i>"
    document['offset'].html = int(document['offset'].html) + 7
    aio.run(search_by_time(document['teacher-id'].html, False))

def this_week(vars):
    document['this-week'].html = "<i>Loading...</i>"
    document['offset'].html = 0
    aio.run(search_by_time(document['teacher-id'].html, False))

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
    document['back-to-subject'].html = """<a href="/schedule.html"><i>Back</i></a>"""

    document['clicky-slider'].html = slider_html
    document["switch-tutor"].bind("mousedown", toggle_bind)

    document["switch-tutor"].click()

    document['results'].html = tutor_template
    aio.run(search_by_tutor())
    # toggle_bind()

def subject_chooser():
    document['clicky-slider'].html = ""

    document['results'].html = """<h2>Pick a Subject:</h2><a href="#" onclick="return false;"><i class="subject-button" id="All Subjects">All Subjects</i></a>&nbsp&nbsp"""

    for s in SUBJECTS:
        document['results'].html += """<a href="#" onclick="return false;"><i class="subject-button" id="{subject}">{subject}</i></a>&nbsp&nbsp""".format(subject=s)

    for d in document.select(".subject-button"):
        d.bind("click", pick_subject)

# document["switch-tutor"].bind("mousedown", toggle_bind)
subject_chooser()
