from browser import document, alert, aio, bind, window
import javascript

URL = "https://api.tadpoletutoring.org"

default_session_table_header = """
<tr>
    <th>Session ID</td>
    <th>Teacher Name</th>
    <th>Start Time</th>
    <th>Date</th>
    <th>Teacher's Subjects</th>
</tr>"""

empty_session_table_header = """
<tr>
    <th>You have no sessions!</th><th><a href="/schedule.html">Browse Available Sessions</a></th>
</tr>"""

session_table_entry_template = """
<tr>
    <td>{id}</td>
    <td>{first_name} {last_name}</td>
    <td>{start_time}</td>
    <td>{date_str}</td>
    <td>{subjects}</td>
</tr>"""

def calculate_timezone_offset():
    date = javascript.Date.new()
    return int(date.getTimezoneOffset())

def deserialize(obj_str):
    return javascript.JSON.parse(obj_str)

def get_cookies():
    cookie_list = document.cookie.split('; ')
    cookie_dict = dict()
    for c in cookie_list:
        if c == "":
            continue
        cookie_tuple = c.split('=')
        cookie_dict.update({cookie_tuple[0]: cookie_tuple[1].replace('"', '')})
    return cookie_dict

async def fetch_api(endpoint="/api/search-times", params={}, get_response=True):
    """
    Fetches stuff from any API endpoint
    """

    params.update(get_cookies())

    req = await aio.get(URL + endpoint, data=params)

    if get_response:
        response = deserialize(req.data)
        return response



def add_template_to_table(params):
    template_html = session_table_entry_template.format(**params)
    document['session-table'].html += template_html

async def add_sessions_to_table():
    document['session-table'].html = default_session_table_header

    user_sessions = await fetch_api("/api/get-user-times", {"tz_offset": calculate_timezone_offset()})

    if len(user_sessions) == 0:
        document['session-table'].html = empty_session_table_header
    else:
        for session in user_sessions:
            session['subjects'] = session['subjects'].replace("|", ", ")
            add_template_to_table(session)

aio.run(add_sessions_to_table())