from browser import document, alert, aio, bind
import javascript

cart_entry_template = """<tr>
    <td>{id}</td>
    <td>{teacher}</td>
    <td>{time}</td>
    <td><a class="remove" id="{id}" href="#" onclick="return false;">Remove From Cart</a></td>
</tr>"""

default_cart_contents = document['cart-table'].html

def deserialize(obj_str):
    return javascript.JSON.parse(obj_str)

async def fetch_api(endpoint="/api/search-times", params={}, get_response=True):
    """
    Fetches stuff from any API endpoint
    """
    # URL = "http://localhost:5000"
    URL = "https://api.tadpoletutoring.org"

    req = await aio.get(URL + endpoint, data=params)

    if get_response:
        response = deserialize(req.data)
        return response

def remove_from_cart(vars):
    remove_id = int(vars.target.id)
    aio.run(remove_id_and_update(remove_id))

async def remove_id_and_update(id):
    await fetch_api("/api/remove-from-cart", {"time_id": id}, False)
    await add_cart_to_table()

def add_template_to_table(id, teacher, time):
    template_html = cart_entry_template.format(id=str(id), teacher=teacher, time=time)
    document['cart-table'].html += template_html
    # document['remove' + str(id)].bind("click", remove_from_cart)

def calculate_timezone_offset():
    date = javascript.Date.new()
    return int(date.getTimezoneOffset())

async def add_cart_to_table():
    document['cart-table'].html = default_cart_contents

    cart_items = await fetch_api("/api/get-cart", {"tz_offset": calculate_timezone_offset()})

    for entry in cart_items:
        add_template_to_table(entry['id'], entry['first_name'] + " " + entry["last_name"], entry['start_time'])

    for d in document.select(".remove"):
        d.bind("click", remove_from_cart)

aio.run(add_cart_to_table())