import os
import secrets
from datetime import datetime, timedelta

import flask
import pytz

import stripe

import api
import database
import notify
import views
from flask_cors import CORS

from flask import Flask, redirect, url_for, request, make_response, session, render_template, Markup, jsonify
from flask_dance.contrib.google import make_google_blueprint, google

import auth
from config import *
import cognito
from utils.log import log_info

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
CORS(app)

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

stripe.api_key = STRIPE_API_KEY

@app.route('/')
def index():
    state = {}
    email = auth.check_login(request) # do stuff with this
    if email:
        state['logged_in'] = True
    # return render_template("index.html", navbar=views.render_navbar(state))
    return render_template("index.html")

@app.route('/login')
def login():
    """
    Redirects to the proper login page (right now /google/login), but may change
    """
    if not auth.check_login(request):
        return redirect(cognito.get_login_url())
    else:
        url = request.headers.get("Referer")
        return redirect(url)

@app.route('/check', methods = ['POST'])
def check_login():
    if auth.check_login(request):
        return "Success!"
    else:
        return ""

@app.route('/populate-index')
def populate_index():
    db = database.Database()

    db.init_db_connection()

    midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    db.add_student('student1@email.com', "student1", "studentOne")
    db.add_student('student2@email.com', "student2", "studentTwo")
    db.add_student('student3@email.com', "student3", "studentThree")
    db.add_student('student4butactuallyteacher@email.com', "student4", "studentFour")
    db.make_teacher('student4butactuallyteacher@email.com', [], "", 0)
    db.add_teacher("teacher1@email.com", "teacher1", "teacherOne", ["English"], "", 0)
    db.add_teacher("teacher2@email.com", "teacher2", "teacherTwo", ["English", "Math"], "", 0)
    db.add_teacher("teacher3@email.com", "teacher3", "teacherThree", ["Math"], "", 0)
    db.add_time_for_tutoring("teacher1@email.com", midnight)
    db.add_time_for_tutoring("teacher2@email.com", midnight + timedelta(days=1))
    db.add_time_for_tutoring("teacher1@email.com", midnight + timedelta(days=2))
    db.add_time_for_tutoring("teacher2@email.com", midnight + timedelta(days=3))

    db.append_cart('student1@email.com', 1)
    db.append_cart('student1@email.com', 2)

    db.end_db_connection()

    return "done"

@app.route('/callback')
def callback():
    """
    Processes callback from AWS Cognito
    """
    user_info = cognito.check_callback(request)
    if user_info: # todo add more checks
        # response = make_response(render_template("index.html", navbar=views.render_navbar({})))
        response = make_response(render_template("index.html"))

    return auth.set_login(response, user_info)

@app.route('/logout')
def logout():
    auth.deauth_token(request)
    session.clear()
    response = make_response(render_template("index.html"))
    response.set_cookie("email", expires=0)
    response.set_cookie("token", expires=0)
    return response

@app.route('/api/register')
def api_register_student():
    if api.register_student(request):
        return api.serialize({})

    return flask.abort(500)

@app.route('/api/person')
def api_get_person():
    user_data = api.get_person(request)

    log_info(user_data)

    return api.serialize(user_data)

    # return flask.abort(500)

@app.route('/api/teachers', methods=['POST'])
def api_fetch_teachers():
    teachers = list(api.fetch_teachers())
    return api.serialize(teachers)

@app.route('/api/search-times', methods=['POST'])
def api_search_times():
    timezone_offset = timedelta(minutes=request.form.get("tz_offset", 0, int))

    teacher_email = request.form.get("teacher_email", None, str)
    subject = request.form.get("subject", None, str)
    must_be_unclaimed = request.form.get("must_be_unclaimed", True, bool)

    search_params = {
        "teacher_email": teacher_email,
        "subject": subject,
        "must_be_unclaimed": must_be_unclaimed
    }

    db = database.Database()

    db.init_db_connection()
    times = db.get_time_schedule(timezone_offset, search_params=search_params)
    db.end_db_connection()

    return api.serialize(times)

@app.route('/api/update-time')
def api_update_time():
    if api.update_time(request):
        return api.serialize({})

    return flask.abort(500)

@app.route('/api/add-to-cart')
def api_add_to_cart():
    if email := auth.check_login(request):
        time_id = request.form.get('id', None, int)

        if time_id is None:
            return flask.abort(400)

        db = database.Database()

        db.init_db_connection()
        # if not db.time
        db.append_cart(email, time_id)
        cart = db.get_cart(email)
        db.end_db_connection()

        return api.serialize(cart)

    log_info("Not logged in")
    return flask.abort(500)

@app.route('/api/make-teacher')
def api_make_teacher():
    if email := auth.check_login(request):
        # TODO Check if email is authorized to make this change

        return api.make_teacher(request)

    return flask.abort(500)

# @app.route('/api/claim-time')
# def api_claim_time():
#     if api.claim_time(request):
#         return api.pickle_str({})
#
#     return flask.abort(500)

@app.route('/api/create-payment-intent', methods=['POST'])
def create_payment():
    if email := auth.check_login(request):
        db = database.Database()

        db.init_db_connection()
        cart, intent = db.get_cart(email)
        db.end_db_connection()

        if intent != "":
            log_info("Intent " + intent + " already created. Aborting.")
            return flask.abort(500)

        num_sessions = len(cart)

        rate = 2100

        if num_sessions == 2:
            rate = 2300

        if num_sessions == 1:
            rate = 2500

        if num_sessions <= 0:
            log_info("Invalid number of sessions specified " + email + " " + str(cart))
            return flask.abort(400)

        intent = stripe.PaymentIntent.create(
            amount=rate * num_sessions,
            currency='usd'
        )

        db.init_db_connection()
        db.set_intent(email, intent.get('id'))
        db.end_db_connection()

        try:
            # Send publishable key and PaymentIntent details to client
            return jsonify({'publishableKey': STRIPE_PUBLISHABLE_KEY, 'clientSecret': intent.client_secret, 'intentId': intent.get('id')})
        except Exception as e:
            return jsonify(error=str(e)), 403

    log_info("Not logged in")
    return ""


@app.route('/api/handle-payment', methods=['POST'])
def handle_payment():
    if email := auth.check_login(request):
        intent_id = request.form.get("intentId")

        if not intent_id:
            log_info("No intentId passed " + str(request.args) + " " + str(request.form))
            return ""

        intent = stripe.PaymentIntent.retrieve(intent_id)

        if intent['amount_received'] >= intent['amount']:
            log_info("Amount Paid: " + str(intent['amount_received']) + " cents")

            db = database.Database()

            db.init_db_connection()
            cart, intent = db.get_cart(email)
            db.end_db_connection()

            if intent_id == intent:
                log_info("Server cart matches intent cart, claiming times...")
                db.init_db_connection()
                for t_id in cart:
                    db.claim_time(email, t_id)

                db.set_cart(email, set())
                db.end_db_connection()
                log_info("Times claimed")

                notify_email = notify.Email()
                notify_email.send(email, "Order Confirmation")

        return ""

    log_info("Not logged in")
    return ""


if __name__ == '__main__':
    app.run()
