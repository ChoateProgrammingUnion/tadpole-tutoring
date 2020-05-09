from browser import document, alert, aio, bind
import javascript
from config import URL

cart_entry_template = """<tr>
    <td>{id}</td>
    <td>{first_name} {last_name}</td>
    <td>{start_time}</td>
    <td>{date_str}</td>
    <td>{subjects}</td>
    <td><a class="remove" id="{id}" href="#" onclick="return false;">Remove From Cart</a></td>
</tr>"""

default_cart_table_contents = """<tr>
    <th>Session ID</th>
    <th>Teacher</th>
    <th>Time</th>
    <th>Date</th>
    <th>Subjects</th>
</tr>"""

empty_cart_table_contents = """<tr>
    <th>Your Cart Is Empty!</th><th><a href="/schedule.html">Browse Sessions</a></th>
</tr>"""

def deserialize(obj_str):
    return javascript.JSON.parse(obj_str)

async def fetch_api(endpoint="/api/search-times", params={}, get_response=True):
    """
    Fetches stuff from any API endpoint
    """

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

def add_template_to_table(params):
    template_html = cart_entry_template.format(**params)
    document['cart-table'].html += template_html
    # document['remove' + str(id)].bind("click", remove_from_cart)

def calculate_timezone_offset():
    date = javascript.Date.new()
    return int(date.getTimezoneOffset())

async def add_cart_to_table():
    document['cart-table'].html = default_cart_table_contents

    cart_items = await fetch_api("/api/get-cart", {"tz_offset": calculate_timezone_offset()})

    if len(cart_items) == 0:
        document['cart-table'].html = empty_cart_table_contents
        return

    for entry in cart_items:
        entry['subjects'] = entry['subjects'].replace("|", ", ")
        add_template_to_table(entry)

    for d in document.select(".remove"):
        d.bind("click", remove_from_cart)

aio.run(add_cart_to_table())
