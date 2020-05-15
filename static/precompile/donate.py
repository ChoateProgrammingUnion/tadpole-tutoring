from browser import document, alert, aio, bind, window
import javascript
URL = "http://localhost:5000"

payment_template = """
"""

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

def set_price(price):
    window.setupPayment(price)

set_price(1000)