from browser import document, alert, aio
import javascript
# from browser.template import Template
# import browser
# from browser.template import Template
# import urllib.request
# import urllib.parse
# import base64
# import javascript

cart_entry_template = """<tr>
    <td>{id}</td>
    <td>{teacher}</td>
    <td>{time}</td>
    <td><a id="remove{id}" href="#" onclick="return false;">Remove From Cart</a></td>
</tr>"""

def deserialize(obj_str):
    return javascript.JSON.parse(obj_str)

async def fetch_api(endpoint="/api/search-times", params={}):
    """
    Fetches stuff from any API endpoint
    """
    URL = "http://localhost:5000"
    # URL = "http://api.tadpoletutoring.org"

    req = await aio.post(URL + endpoint, data=params)
    response = deserialize(req.data)

    return response

def remove_from_cart(vars):
    remove_id = vars.target.id
    alert(remove_id)

def add_template_to_table(id, teacher, time):
    template_html = cart_entry_template.format(id=str(id), teacher=teacher, time=time)
    document['cart-table'].html += template_html
    document['remove' + str(id)].bind("mousedown", remove_from_cart)

async def add_cart_to_table():
    cart_ids = await fetch_api("/api/get-cart")

    for i in cart_ids:
        add_template_to_table(i, "Teach", "8:00 PM")

aio.run(add_cart_to_table())