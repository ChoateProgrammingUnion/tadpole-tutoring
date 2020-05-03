import os
import secrets

import flask

import api
import views

from flask import Flask, redirect, url_for, request, make_response, session, render_template, Markup
from flask_dance.contrib.google import make_google_blueprint, google

import auth
from config import *
import cognito


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
    state = {}
    email = auth.check_login(request) # do stuff with this
    if email:
        state['logged_in'] = True
    return render_template("index.html", navbar=views.render_navbar(state))

@app.route('/login')
def login():
    """
    Redirects to the proper login page (right now /google/login), but may change
    """
    if not auth.check_login(request):
        return redirect(cognito.get_login_url())
    else:
        return "You are logged in!"

@app.route('/callback')
def callback():
    """
    Processes callback from AWS Cognito
    """
    user_info = cognito.check_callback(request)
    if user_info: # todo add more checks
        response = make_response(render_template("index.html", navbar=views.render_navbar({})))

    return auth.set_login(response, user_info)

@app.route('/logout')
def logout():
    auth.deauth_token(request)
    session.clear()
    return redirect("/")


@app.route('/api/register')
def api_register_student():
    if api.register_student(request):
        return {}

    return flask.abort(500)

@app.route('/api/person')
def api_get_person():
    if user_data := api.get_person(request):
        return user_data

    return flask.abort(500)

@app.route('/api/teachers')
def api_fetch_teachers():
    return api.fetch_teachers()

@app.route('/api/update-time')
def api_update_time():
    if api.update_time(request):
        return {}

    return flask.abort(500)

@app.route('/api/make-teacher')
def api_make_teacher():
    if api.make_teacher(request):
        return {}

    return flask.abort(500)

@app.route('/api/claim-time')
def api_claim_time():
    if api.claim_time(request):
        return {}

    return flask.abort(500)


if __name__ == '__main__':
    app.run()
