from browser import document, alert, aio
import javascript
from config import URL

teacher_profile_form = """
<form action="/teacher">
    <header>
        <h2>Account Settings</h2>
    </header>

    <label>Subjects:</label>

    <input type="checkbox" id="focus-price" name="math" value="Math">
    <label for="focus-price">Math</label>

    <input type="checkbox" id="focus-service" name="english" value="English">
    <label for="focus-service">English</label>

    <input type="checkbox" id="focus-service" name="cs" value="CS (Computer Science)">
    <label for="focus-service">Computer Science</label>

    <label for="bio">Bio:</label>

    <textarea cols="40" rows="5" id="bio"></textarea>
    <button type="submit">Save</button>
</form>
"""

claim_teacher_button = """
<form action="/api/claim-teacher">
    <button type="submit">I am a teacher</button>
</form>
"""

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

async def load_settings_page():
    """
    Loads setting page and checks if student or teacher
    """
    # is_teacher = await check_teacher()
    is_teacher = check_teacher()
    if is_teacher:
        document['user-settings'].html = teacher_profile_form
    else:
        document['user-settings'].html = claim_teacher_button

    return True

async def check_teacher():
    teachers = await fetch_teachers()
    print(teachers)
    if not document.cookie.get("email"):
        # TODO: redirect to login!
        print("Not logged in")
    else:
        if document.get("email"):
            print(document.get("email"))
            for each_teacher in teachers:
                if document.get("email").rstrip() == each_teacher.get("email"):
                    return True
    return False

aio.run(load_settings_page())