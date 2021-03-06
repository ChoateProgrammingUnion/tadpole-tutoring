from browser import document, alert, aio, window
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

student_profile_form = """
<section>
<form action="javascript:void(0);" id='inner-form'>
    <h2><u>Account Settings</u></h2>

    <label for="hours">First Name:</label>
    <input maxlength="100" type="text" id="first_name" name="first_name" size="28" placeholder="{first_name}">

    <label for="hours">Last Name:</label>
    <input maxlength="100" type="text" id="last_name" name="last_name" size="28" placeholder="{last_name}">

    <label for="hours">Phone Number:</label>
    <input maxlength="100" type="text" id="phone_number" name="phone_number" size="28" placeholder="{phone_number}">

    <label for="hours">WeChat Account:</label>
    <input maxlength="100" type="text" id="wechat" name="wechat" size="28" placeholder="{wechat}">
    
    <button id="save-settings">Save</button>
</form>
</section>
"""

teacher_profile_form_start = """
<section>
<a href="create.html"><i>Create Session</i></a>
</section>

<section>
<form action="javascript:void(0);" id='inner-form'>
    <h2><u>Account Settings</u></h2>

    <label for="hours">First Name:</label>
    <input type="text" id="first_name" name="first_name" size="28" placeholder="{first_name}">

    <label for="hours">Last Name:</label>
    <input type="text" id="last_name" name="last_name" size="28" placeholder="{last_name}">
    
    <label for="hours">Phone Number:</label>
    <input type="text" id="phone_number" name="phone_number" size="28" placeholder="{phone_number}">

    <label for="hours">Zoom link:</label>
    <input type="text" id="zoom" name="zoom" size="28" placeholder="{zoom_id}">

    <label for="hours">Link to a Photo of You:</label>
    <input type="text" id="icon" name="icon" size="28" placeholder="{icon}">

    <label for="hours">Maximum Hours Per Week:</label>
    <input type="text" id="max_hours" name="max_hours" size="28" placeholder="{max_hours}">

    <label>Subjects:</label>
</form>
</section>
"""

teacher_profile_subject_template = """
    <input type="checkbox" class="form-checkbox" id="{subject}" name="{subject}" value="{subject}">
    <label for="focus-price">{subject}</label>
    <br>
"""

teacher_profile_subject_template_checked = """
    <input type="checkbox" class="form-checkbox" id="{subject}" name="{subject}" value="{subject}" checked="">
    <label for="focus-price">{subject}</label>
    <br>
"""

teacher_profile_form_end = """
    <label for="bio">Bio:</label>

    <textarea cols="40" rows="5" id="bio" placeholder="{bio}"></textarea>
    <button id="save-settings">Save</button>
"""

null = """
    <label for="hours">Max hours:</label>
    <input type="number" id="hours" name="hours" size="28" placeholder="3">
"""

claim_teacher_button = """
<br><br>
<center>
<button id="claim-teacher">I am a teacher</button>
<input type="text" id="teacher-secret" size="28" placeholder="Teacher Secret Password">
</center>
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

async def rename_teacher():
    # await fetch_api('/api/claim-teacher')
    succeeded = await fetch_api('/api/make-teacher', {"pass": document['teacher-secret'].value})
    if succeeded:
        alert("You are now a teacher!")
        await load_settings_page()
    else:
        alert("Wrong Password!")

def rename_teacher_run(vars):
    aio.run(rename_teacher())

def document_get(value):
    try:
        return document[value]
    except:
        return ""

async def submit_form():
    is_teacher = await check_teacher()

    if is_teacher:
        subjects_str = ""

        params = dict()

        for d in document.select(".form-checkbox"):
            if d.checked:
                subjects_str += d.value + "|"

        subjects_str = subjects_str[:-1]

        params.update({"subjects": subjects_str})

        bio = document['bio'].value
        phone_number = document['phone_number'].value

        first_name = document['first_name'].value
        last_name = document['last_name'].value

        zoom = document['zoom'].value
        max_hours = document['max_hours'].value

        icon = document['icon'].value

        if first_name != "": params.update({"first_name": first_name})
        if last_name != "": params.update({"last_name": last_name})
        if bio != "": params.update({"bio": bio})
        if zoom != "": params.update({"zoom_id": zoom})
        if max_hours != "": params.update({"max_hours": int(max_hours)})
        if phone_number != "": params.update({"phone_number": phone_number})
        if icon != "": params.update({"icon": icon})

        await fetch_api("/api/edit-teacher", params)
    else:
        params = dict()

        first_name = document['first_name'].value
        last_name = document['last_name'].value

        wechat = document['wechat'].value
        phone_number = document['phone_number'].value

        if first_name != "": params.update({"first_name": first_name})
        if last_name != "": params.update({"last_name": last_name})
        if wechat != "": params.update({"wechat": wechat})
        if phone_number != "": params.update({"phone_number": phone_number})

        await fetch_api("/api/edit-student", params)

    alert("Your profile has been updated!")

def submit_form_run(vars):
    aio.run(submit_form())

async def load_settings_page():
    """
    Loads setting page and checks if student or teacher
    """
    is_teacher = await check_teacher()
    # is_teacher = check_teacher()
    if is_teacher:
        teacher_details = await fetch_api('/api/get-teacher-by-email')

        if 'icon' not in teacher_details:
            teacher_details['icon'] = 'https://github.com/identicons/jasonlong.png'

        if 'max_hours' not in teacher_details:
            teacher_details['max_hours'] = 1

        if 'phone_number' not in teacher_details:
            teacher_details['phone_number'] = '000-000-0000'

        document['user-settings'].html = teacher_profile_form_start.format(**teacher_details)
        teacher_subjects = teacher_details['subjects'].split("|")

        for subject in SUBJECTS:
            if subject in teacher_subjects:
                document['inner-form'].html += teacher_profile_subject_template_checked.format(subject=subject)
            else:
                document['inner-form'].html += teacher_profile_subject_template.format(subject=subject)

        document['inner-form'].html += teacher_profile_form_end.format(**teacher_details)

        document['save-settings'].bind("mousedown", submit_form_run)
    else:
        student_details = await fetch_api('/api/get-student-by-email')

        # alert(student_details)

        if 'first_name' not in student_details:
            student_details['first_name'] = ""
        if 'last_name' not in student_details:
            student_details['last_name'] = ""
        if 'phone_number' not in student_details:
            student_details['phone_number'] = ""
        if 'wechat' not in student_details:
            student_details['wechat'] = ""

        document['user-settings'].html = student_profile_form.format(**student_details)
        document['user-settings'].html += claim_teacher_button
        document['save-settings'].bind("mousedown", submit_form_run)

    document['claim-teacher'].bind("mousedown", rename_teacher_run)


async def check_teacher():
    return await fetch_api("/api/check-teacher")
    # return await fetch_api("/api/make-teacher")

aio.run(load_settings_page())
