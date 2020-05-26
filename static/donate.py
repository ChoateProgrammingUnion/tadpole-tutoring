from browser import document, alert, aio, bind, window
import javascript
URL = "{URL}"

payment_template = """
<form id="payment-form" class="sr-payment-form">
    <label>Enter Information Below to Donate ${price:0.2f}</label>
    <br>
    <div class="sr-combo-inputs-row">
        <div class="sr-input sr-card-element" id="card-element">Loading...</div>
    </div>
    <div class="sr-field-error" id="card-errors" role="alert"></div>
    <br>
    <button id="submit">
        <span id="button-text">Pay</span><span id="order-amount"></span>
    </button>
</form>
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

def handle_payment_request(pay):
    document['button-text'].html = "Processing..."
    pay(document['name'].value)

def handle_payment(intent_id, name):
    document['payment-area'].html = ""
    document['donate-button'].html = "Donate"
    aio.run(fetch_api("/api/handle-payment-donation", {"intentId": intent_id, "name": name}, False))
    alert("Thank you for your donation!")

def handle_error():
    document['button-text'].html = "Pay"

def handle_donate_button(vars):
    try:
        amount = float(document['amount'].value)
        assert amount >= 0.50
    except:
        alert("There was an error processing your request. Please ensure that your donation amount is valid.")
    else:
        document['payment-area'].html = payment_template.format(price=amount)
        document['donate-button'].html = "Change Price"
        set_price(amount)


window.handle_payment_request = handle_payment_request
window.handle_payment = handle_payment
window.handle_error = handle_error
document['donate-button'].bind("click", handle_donate_button)