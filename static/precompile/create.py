from browser import document, alert, aio, bind, window
import javascript

URL = https://api.tadpoletutoring.org

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

async def post_form_result():
    params = {"tz_offset": calculate_timezone_offset()}

    for d in document.select(".form-textbox"):
        params.update({d.id: d.value})

    await fetch_api('/api/create-time', params)

def post_form_result_run(vars):
    aio.run(post_form_result())

document['submit-button'].bind('click', post_form_result_run)