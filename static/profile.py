from browser import document, alert, aio
import javascript
from config import URL

teacher_profile_form = """
<section>
<a href="create.html"><i>Create Session</i></a>
</section>

<section>
<form action="/teacher">
    <header>
        <h2>Account Settings</h2>
    </header>

    <label for="hours">Zoom link:</label>
    <input type="text" id="zoom" name="zoom" size="28" placeholder="https://zoom.us/j/0000000">

    <label>Subjects:</label>

    <input type="checkbox" id="focus-price" name="math" value="Math">
    <label for="focus-price">Math</label>

    <input type="checkbox" id="focus-service" name="english" value="English">
    <label for="focus-service">English</label>

    <input type="checkbox" id="focus-service" name="cs" value="cs">
    <label for="focus-service">Computer Science</label>

    <label for="bio">Bio:</label>

    <textarea cols="40" rows="5" id="bio"></textarea>
    <button type="submit">Save</button>
</form>
</section>
"""
null = """
    <label for="hours">Max hours:</label>
    <input type="number" id="hours" name="hours" size="28" placeholder="3">
"""

claim_teacher_button = """
<button id="claim-teacher">I am a teacher</button>
"""
def get_cookies():
    cookie_list = document.cookie.split('; ')
    cookie_dict = dict()
    for c in cookie_list:
        if c == "":
            continue
        cookie_tuple = c.split('=')
        cookie_dict.update({cookie_tuple[0]: cookie_tuple[1].replace('"', '')})
    return cookie_dict

def deserialize(obj_str):
    return javascript.JSON.parse(obj_str)

async def fetch_api(endpoint="/api/search-times", params={}):
    """
    Fetches stuff from any API endpoint
    """
    req = await aio.get(URL + endpoint, data=params)
    response = deserialize(req.data)

    return response

async def fetch_teachers():
    response_dict = await fetch_api("/api/teachers")
    return response_dict

async def fetch_api(endpoint="/api/search-times", params={}):
    """
    Fetches stuff from any API endpoint
    """
    params.update(get_cookies())

    req = await aio.get(URL + endpoint, data=params)
    response = deserialize(req.data)

    return response

async def post_form_result():
    # await fetch_api('/api/claim-teacher')
    await fetch_api('/api/make-teacher', {"pass": document['teacher-secret'].text})

def post_form_result_run(vars):
    aio.run(post_form_result())

async def load_settings_page():
    """
    Loads setting page and checks if student or teacher
    """
    is_teacher = await check_teacher()
    # is_teacher = check_teacher()
    if is_teacher:
        document['user-settings'].html = teacher_profile_form
    else:
        document['user-settings'].html = claim_teacher_button

    document['claim-teacher'].bind("mousedown", post_form_result_run)

    return True

async def check_teacher():
    return await fetch_api("/api/check-teacher")
    # return await fetch_api("/api/make-teacher")

aio.run(load_settings_page())
