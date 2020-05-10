from browser import document, alert, aio, bind, window
import javascript
URL = "{URL}"

cart_entry_template = """
<tr>
    <td>{id}</td>
    <td>{first_name} {last_name}</td>
    <td>{start_time}</td>
    <td>{date_str}</td>
    <td>{subjects}</td>
    <td><a class="remove" id="{id}" href="#" onclick="return false;">Remove From Cart</a></td>
</tr>"""

default_cart_table_template = """
<tr>
    <th>Session ID</th>
    <th>Teacher</th>
    <th>Time</th>
    <th>Date</th>
    <th>Subjects</th>
</tr>"""

empty_cart_table_template = """
<tr>
    <th>Your Cart Is Empty!</th><th><a href="/schedule.html">Browse Sessions</a></th>
</tr>"""


default_checkout_table_template = """
<tr>
    <th>Session</th>
    <th>Price</th>
</tr>"""

empty_checkout_table_template = """"""

checkout_table_entry_template = """
<tr>
    <td>Tutoring Session #{id}</td>
    <td>$25.00</td>
</tr>"""

checkout_table_total_template = """
<tr>
    <th>TOTAL</th>
    <th>${price}.00</th>
</tr>"""

checkout_table_discount_template = """
<tr>
    <th>Discount</th>
    <th>-${price}.00</th>
</tr>"""

payment_template = """
<form id="payment-form" class="sr-payment-form">
    <div class="sr-combo-inputs-row">
        <div class="sr-input sr-card-element" id="card-element"></div>
    </div>
    <div class="sr-field-error" id="card-errors" role="alert"></div>
    <button id="submit">
        <span id="button-text">Pay</span><span id="order-amount"></span>
    </button>
</form>"""

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

def gen_checkout_table(cart_items):
    num_items = len(cart_items)
    total_price = 25 * num_items

    if num_items == 0:
        document['checkout-table'].html = empty_checkout_table_template
        document['checkout-label'].html = ""
        return

    document['checkout-table'].html = default_checkout_table_template
    document['checkout-label'].html = "Checkout"

    for entry in cart_items:
        document['checkout-table'].html += checkout_table_entry_template.format(**entry)

    if num_items == 2:
        document['checkout-table'].html += checkout_table_discount_template.format(price=2*num_items)
        total_price -= 2 * num_items

    elif num_items > 2:
        document['checkout-table'].html += checkout_table_discount_template.format(price=4*num_items)
        total_price -= 4 * num_items

    document['checkout-table'].html += checkout_table_total_template.format(price=total_price)

async def add_cart_to_table():
    document['cart-table'].html = default_cart_table_template

    cart_items = await fetch_api("/api/get-cart", {"tz_offset": calculate_timezone_offset()})

    if len(cart_items) == 0:
        document['cart-table'].html = empty_cart_table_template
        document['payment-area'].html = ""
    else:
        document['payment-area'].html = payment_template
        window.setupPayment()
        for entry in cart_items:
            entry['subjects'] = entry['subjects'].replace("|", ", ")
            add_template_to_table(entry)

        for d in document.select(".remove"):
            d.bind("click", remove_from_cart)

    gen_checkout_table(cart_items)

def handle_payment_run(intentId):
    aio.run(handle_payment(intentId))

async def handle_payment(intentId):
    success = await fetch_api("/api/handle-payment", {"intentId": intentId})

    if success:
        alert("Your times have been claimed!")
    else:
        alert("An error has occurred")

    await add_cart_to_table()

def verify_cart_run(pay):
    aio.run(verify_cart(pay))

async def verify_cart(pay):
    verified = await fetch_api("/api/verify-cart")

    if verified:
        pay()
    else:
        alert("Some of your cart items have already been bought")
        await add_cart_to_table()

window.verify_cart = verify_cart_run
window.handle_payment = handle_payment_run
window.get_cookies = get_cookies
aio.run(add_cart_to_table())
