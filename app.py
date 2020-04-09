import os
import secrets

from flask import Flask, redirect, url_for, request, make_response, session
from flask_dance.contrib.google import make_google_blueprint, google

import auth
from config import *

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)

random_secret_key = secrets.token_urlsafe(32)
app.config.update(
    DEBUG=False,
    SECRET_KEY=random_secret_key
)

# Credit: oauth boilerplate stuff from library documentation
app.config["GOOGLE_OAUTH_CLIENT_ID"] = GOOGLE_CLIENT_ID
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = GOOGLE_CLIENT_SECRET
app.config["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "true"
app.config['SERVER_NAME'] = SERVER_NAME
app.config['PREFERRED_URL_SCHEME'] = "https"
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "true"

google_bp = make_google_blueprint(scope=["https://www.googleapis.com/auth/userinfo.profile",
                                         "https://www.googleapis.com/auth/userinfo.email"], offline=True)

app.register_blueprint(google_bp, url_prefix="/login")

@app.route('/')
def index():
    email, first_name, last_name = auth.check_login(request)

    if not(email and first_name and last_name):
        return redirect("/login")

    response = make_response("Hello " + first_name + " " + last_name)

    return auth.set_login(response, request)


@app.route('/login')
def login():
    """
    Redirects to the proper login page (right now /google/login), but may change
    """
    if (not google.authorized) or auth.get_token(request):
        return redirect(url_for("google.login"))
    else:
        resp = make_response("Invalid credentials! Make sure you're logging in with your Choate account. "
                             "<a href=\"/logout\">Try again.</a>")
        return resp


@app.route('/logout')
def logout():
    auth.deauth_token(request)
    session.clear()
    return redirect("/")


if __name__ == '__main__':
    app.run()
