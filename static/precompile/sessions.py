from browser import document, alert, aio, bind, window
import javascript

URL = "http://localhost:5000"

default_session_table_header = """
<tr>
    <th>Session ID</td>
    <th>Teacher Name</th>
    <th>Start Time</th>
    <th>Date</th>
    <th>Zoom Link</th>
</tr>"""

empty_session_table_header = """
<tr>
    <th>You have no sessions!</th><th><a href="/schedule.html">Browse Available Sessions</a></th>
</tr>"""

session_table_entry_template = """
<tr>
    <td>{_id}</td>
    <td>{first_name} {last_name}</td>
    <td>{start_time}</td>
    <td>{date_str}</td> 
    <td>{zoom_id}</td> 
</tr>"""

default_session_table_header_teacher = """
<tr>
    <th>Session ID</td>
    <th>Start Time</th>
    <th>Date</th>
    <th>Claimed By</th>
    <th></th>
</tr>"""

empty_session_table_header_teacher = """
<tr>
    <th>You have created no sessions!</th><th><a href="/create.html">Create a Session</a></th>
</tr>"""

session_table_entry_template_teacher = """
<tr>
    <td>{_id}</td>
    <td>{start_time}</td>
    <td>{date_str}</td>
    <td>{student}</td>
    <td>{remove-button}</td>
</tr>"""

remove_button_template = """<a class="remove" id="{_id}" href="#" onclick="return false;">Remove Session</a>"""

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



def add_template_to_table(params, is_teacher):
    if is_teacher:
        if params['claimed']:
            params['remove-button'] = ''
        else:
            params['remove-button'] = remove_button_template.format(**params)

        template_html = session_table_entry_template_teacher.format(**params)
    else:
        template_html = session_table_entry_template.format(**params)
    document['session-table'].html += template_html


def remove_session(vars):
    remove_id = str(vars.target.id)
    aio.run(remove_id_and_update(remove_id))

async def remove_id_and_update(id):
    await fetch_api("/api/remove-session", {"time_id": id}, False)
    await add_sessions_to_table()


async def add_sessions_to_table():
    user_sessions, is_teacher = await fetch_api("/api/get-user-times", {"tz_offset": calculate_timezone_offset()})

    if is_teacher:
        document['session-table'].html = default_session_table_header_teacher

        if len(user_sessions) == 0:
            document['session-table'].html = empty_session_table_header_teacher
        else:
            for session in user_sessions:
                session['subjects'] = session['subjects'].replace("|", ", ")
                if session['student'] == '':
                    session['student'] = 'Nobody'
                add_template_to_table(session, is_teacher)

            for d in document.select(".remove"):
                d.bind("click", remove_session)
    else:
        document['session-table'].html = default_session_table_header

        if len(user_sessions) == 0:
            document['session-table'].html = empty_session_table_header
        else:
            for session in user_sessions:
                session['subjects'] = session['subjects'].replace("|", ", ")
                if session['zoom_id'] != "":
                    session['zoom_id'] = '<a href="{zoom_id}">{zoom_id}</a>'.format(**session)
                add_template_to_table(session, is_teacher)

aio.run(add_sessions_to_table())