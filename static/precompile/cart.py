from browser import document, alert
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

def fetch_api(endpoint="/api/search-times", params={}):
    import urllib.request
    import base64
    import pickle

    URL = "http://localhost:5000"
    # URL = "http://api.tadpoletutoring.org"
    if "teacher_email" in params:
        response_raw = urllib.request.urlopen(URL + endpoint+"?teacher_email=" + params.get("teacher_email")).read().rstrip()
    else:
        response_raw = urllib.request.urlopen(URL + endpoint).read().rstrip()

    response_decode = base64.b64decode(response_raw.encode())
    response = pickle.loads(response_decode)
    return response

def remove_from_cart(vars):
    remove_id = vars.target.id
    alert(remove_id)

def add_template_to_table(id, teacher, time):
    template_html = cart_entry_template.format(id=str(id), teacher=teacher, time=time)
    document['cart-table'].html += template_html
    document['remove' + str(id)].bind("mousedown", remove_from_cart)

print("hello!")
add_template_to_table(0, "Teach", "8:00 PM")