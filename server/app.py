import os
import secrets
from datetime import datetime, timedelta
import time

import flask
import pytz

import stripe

import api
import database
import notify
import views
from flask_cors import CORS

from flask import Flask, redirect, url_for, request, make_response, session, render_template, Markup, jsonify

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
# app.config['SERVER_NAME'] = SERVER_NAME
app.config['PREFERRED_URL_SCHEME'] = "https"
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "true"

stripe.api_key = STRIPE_API_KEY


@app.route('/')
def index():
    state = {}
    email = auth.check_login(request)  # do stuff with this
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
        # url = request.headers.get("Referer")
        return render_template("index.html")


@app.route('/check', methods=['POST'])
def check_login():
    if auth.check_login(request):
        return "Success!"
    else:
        return ""


# @app.route('/populate-index')
# def populate_index():
#     db = database.Database()
#
#     #
#     midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
#
#     db.add_student('student1@email.com', "student1", "studentOne")
#     db.add_student('student2@email.com', "student2", "studentTwo")
#     db.add_student('student3@email.com', "student3", "studentThree")
#     db.add_student('student4butactuallyteacher@email.com', "student4", "studentFour")
#     db.make_teacher('student4butactuallyteacher@email.com', [], "", 0)
#     db.add_teacher("teacher1@email.com", "teacher1", "teacherOne", ["English"], "", 0)
#     db.add_teacher("teacher2@email.com", "teacher2", "teacherTwo", ["English", "Math"], "", 0)
#     db.add_teacher("teacher3@email.com", "teacher3", "teacherThree", ["Math"], "", 0)
#     db.add_time_for_tutoring("teacher1@email.com", midnight)
#     db.add_time_for_tutoring("teacher2@email.com", midnight + timedelta(days=1))
#     db.add_time_for_tutoring("teacher1@email.com", midnight + timedelta(days=2))
#     db.add_time_for_tutoring("teacher2@email.com", midnight + timedelta(days=3))
#
#     db.append_cart('student1@email.com', 1)
#     db.append_cart('student1@email.com', 2)
#
#     #
#     return "done"

@app.route('/callback')
def callback():
    """
    Processes callback from AWS Cognito
    """
    user_info = cognito.check_callback(request)
    if user_info:  # todo add more checks
        # response = make_response(render_template("index.html", navbar=views.render_navbar({})))
        response = make_response(render_template("index.html"))

    return auth.set_login(response, user_info)


@app.route('/logout')
def logout():
    # auth.deauth_token(request)
    session.clear()
    response = make_response(render_template("index.html"))
    response.set_cookie("email", expires=0)
    response.set_cookie("email", domain='tadpoletutoring.org', expires=0)
    response.set_cookie("token", expires=0)
    response.set_cookie("token", domain='tadpoletutoring.org', expires=0)
    return response


@app.route('/api/register')
def api_register_student():
    if api.register_student(request):
        return api.serialize({})

    return flask.abort(500)


@app.route('/api/register-teacher')
def api_register_teacher():
    if auth.check_teacher(request):
        pass

    return flask.abort(405)


@app.route('/api/person')
def api_get_person():
    user_data = api.get_person(request)

    log_info(user_data)

    return api.serialize(user_data)

    # return flask.abort(500)


@app.route('/api/teachers')
def api_fetch_teachers():
    subject = request.args.get("subject", None, str)

    teachers = list(api.fetch_teachers(subject, False))
    return api.serialize(teachers)


@app.route('/api/get-teacher')
def api_get_teacher():
    teacher_id = request.args.get("teacher_id", None, str)

    if teacher_id is None:
        return flask.abort(400)

    db = database.Database()

    teacher = db.get_teacher_by_id(teacher_id)
    return api.serialize(teacher)


@app.route('/api/get-teacher-by-email')
def api_get_teacher_by_email():
    teacher_email = request.args.get("email", None, str)

    if teacher_email is None:
        return flask.abort(400)

    db = database.Database()

    teacher = db.get_teacher(teacher_email)
    return api.serialize(teacher)


@app.route('/api/get-student-by-email')
def api_get_student_by_email():
    student_email = request.args.get("email", None, str)

    if student_email is None:
        return flask.abort(400)

    db = database.Database()

    teacher = db.get_student(student_email)
    return api.serialize(teacher)


@app.route('/api/edit-teacher')
def api_edit_teacher():
    if email := auth.check_login(request):
        subjects = request.args.get("subjects", None, str)
        zoom_id = request.args.get("zoom_id", None, str)
        icon = request.args.get("icon", None, str)
        max_hours = request.args.get("max_hours", None, int)
        bio = request.args.get("bio", None, str)
        first_name = request.args.get("first_name", None, str)
        last_name = request.args.get("last_name", None, str)
        phone_number = request.args.get("phone_number", None, str)

        db = database.Database()

        db.edit_teacher(email, subjects, zoom_id, bio, first_name, last_name, icon, max_hours, phone_number)
        return api.serialize(True)

    return api.serialize(False)


@app.route('/api/edit-student')
def api_edit_student():
    if email := auth.check_login(request):
        first_name = request.args.get("first_name", None, str)
        last_name = request.args.get("last_name", None, str)
        phone_number = request.args.get("phone_number", None, str)
        wechat = request.args.get("wechat", None, str)

        db = database.Database()

        db.edit_student(email, first_name, last_name, phone_number, wechat)
        return api.serialize(True)

    return api.serialize(False)


@app.route('/api/is-teacher-available')
def api_is_teacher_available():
    if email := auth.check_login(request):
        time_id = request.args.get("time_id", None, str)

        if time_id is None:
            log_info("No Time ID Specified!")
            return api.serialize(False)

        db = database.Database()

        t = db.get_time_by_id(time_id)
        teacher_email = t['teacher_email']

        midnight = datetime.fromtimestamp(t['start_time']).astimezone(pytz.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = midnight - timedelta(days=midnight.weekday())
        week_end = week_start + timedelta(days=7)

        return api.serialize(db.check_teacher_availability_for_student(week_start, week_end, teacher_email, email))

    return api.serialize(False)


@app.route('/api/check-teacher')
def api_check_teacher():
    return api.serialize(auth.check_teacher(request))


@app.route('/api/search-times')
def api_search_times():
    timezone_offset = timedelta(minutes=request.args.get("tz_offset", 0, int))

    teacher_email = request.args.get("teacher_email", None, str)
    teacher_id = request.args.get("teacher_id", None, str)
    subject = request.args.get("subject", None, str)
    must_be_unclaimed = request.args.get("must_be_unclaimed", True, bool)

    offset = request.args.get("offset", 0, int)

    search_params = {
        "teacher_email": teacher_email,
        "teacher_id": teacher_id,
        "subject": subject,
        "must_be_unclaimed": must_be_unclaimed
    }

    db = database.Database()

    times = db.get_time_schedule(timezone_offset=timezone_offset, time_offset=timedelta(days=offset),
                                 search_params=search_params)
    return api.serialize(times)


@app.route('/api/get-time')
def api_get_time():
    timezone_offset = timedelta(minutes=request.args.get("tz_offset", 0, int))

    time_id = request.args.get("time_id", None, str)

    if time_id is None:
        return flask.abort(400)

    db = database.Database()

    times = db.get_time_by_id(time_id, timezone_offset, True)
    return api.serialize(times)


@app.route('/api/get-user-times')
def api_get_user_times():
    if email := auth.check_login(request):
        timezone_offset = timedelta(minutes=request.args.get("tz_offset", 0, int))

        is_teacher = auth.check_teacher(request)

        db = database.Database()

        if is_teacher:
            times = db.search_times(teacher_email=email, string_time_offset=timezone_offset, insert_teacher_info=True,
                                    teacher_must_be_available=False, must_be_unclaimed=False)
        else:
            times = db.search_times(student_email=email, string_time_offset=timezone_offset, insert_teacher_info=True,
                                    teacher_must_be_available=False, must_be_unclaimed=False)
        return api.serialize([times, is_teacher])

    return flask.abort(405)


@app.route('/api/update-time')
def api_update_time():
    if api.update_time(request):
        return api.serialize({})

    return flask.abort(500)


@app.route('/api/add-to-cart')
def api_add_to_cart():
    if email := auth.check_login(request):
        time_id = request.args.get('time_id', None, str)

        if time_id is None:
            return flask.abort(400)

        db = database.Database()

        db.append_cart(email, time_id)
        cart, _ = db.get_cart(email)
        return api.serialize(list(cart))

    log_info("Not logged in")
    return flask.abort(500)


@app.route('/api/create-time')
def api_create_time():
    if email := auth.check_login(request):
        date_str = request.args.get('datepicker', "", str) + " " + request.args.get('time-datepicker', "", str)
        timezone_offset = timedelta(minutes=request.args.get("tz_offset", 0, int))
        repeat_option = request.args.get('repeat-option', "none", str)

        log_info("Date String: " + date_str)
        log_info("Timezone Offset: " + str(timezone_offset))

        try:
            d = pytz.utc.localize(datetime.strptime(date_str, '%Y-%m-%d %I:%M %p')) + timezone_offset
        except ValueError:
            log_info(date_str + " failed to serialize")
            try:
                d = pytz.utc.localize(datetime.strptime(date_str, '%m/%d/%y %I:%M %p')) + timezone_offset
            except:
                return flask.abort(400)

        log_info("Serialized Date (UTC): " + str(d))

        db = database.Database()
        db.add_time_for_tutoring(email, d)

        if repeat_option != "none":
            for i in range(int(repeat_option)):
                d += timedelta(days=7)
                db.add_time_for_tutoring(email, d)

        return ""

    log_info("Not logged in")
    return flask.abort(500)


@app.route('/api/verify-cart')
def api_verify_cart():
    if email := auth.check_login(request):
        db = database.Database()

        verified = db.verify_cart(email)
        return api.serialize(verified)

    log_info("Not logged in")
    return flask.abort(500)


@app.route('/api/remove-from-cart')
def api_remove_from_cart():
    if email := auth.check_login(request):
        time_id = request.args.get('time_id', None, str)

        if time_id is None:
            return flask.abort(400)

        db = database.Database()

        cart, _ = db.get_cart(email)
        try:
            cart.remove(time_id)
        except KeyError:
            log_info("Key " + str(time_id) + " not in " + str(cart))
        db.set_cart(email, cart)
        return api.serialize(list(cart))

    log_info("Not logged in")
    return flask.abort(500)


@app.route('/api/remove-session')
def api_remove_remove_session():
    if email := auth.check_login(request):
        time_id = request.args.get('time_id', None, str)

        if time_id is None:
            return flask.abort(400)

        db = database.Database()

        status = db.remove_time(time_id, email)
        return api.serialize(status)

    log_info("Not logged in")
    return flask.abort(500)


@app.route('/api/get-cart')
def api_get_cart():
    if email := auth.check_login(request):
        db = database.Database()

        cart, _ = db.get_cart(email)

        cart_list = []

        for i in cart:
            cart_list.append(db.get_time_by_id(i, timedelta(minutes=request.args.get("tz_offset", 0, int)), True))
        return api.serialize(list(cart_list))

    log_info("Not logged in")
    return flask.abort(500)


@app.route('/api/get-cart-numbers')
def api_get_cart_numbers():
    if email := auth.check_login(request):
        db = database.Database()

        cart, _ = db.get_cart(email)
        return api.serialize(list(cart))

    log_info("Not logged in")
    return flask.abort(500)


@app.route('/api/make-teacher')
def api_make_teacher():
    if secrets.compare_digest(request.args.get('pass').rstrip(), TEACHER_PASSWORD.rstrip()):
        if email := auth.check_login(request):
            db = database.Database()

            db.make_teacher(email, [], "", 0)
            return api.serialize(True)

    return api.serialize(False)


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

        cart, intent = db.get_cart(email)
        # if intent != "":
        #     log_info("Intent " + intent + " already created. Aborting.")
        #     return flask.abort(500)

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

        db.set_intent(email, intent.get('id'))
        try:
            # Send publishable key and PaymentIntent details to client
            return jsonify({'publishableKey': STRIPE_PUBLISHABLE_KEY, 'clientSecret': intent.client_secret,
                            'intentId': intent.get('id')})
        except Exception as e:
            return jsonify(error=str(e)), 403

    log_info("Not logged in")
    return ""


@app.route('/api/create-payment-intent-for-donate', methods=['POST'])
def create_payment_intent_for_donate():
    price = request.json.get('price')

    intent = stripe.PaymentIntent.create(
        amount=int(price * 100),
        currency='usd',
        receipt_email = 'tadpoletutoring123@gmail.com'
    )

    try:
        # Send publishable key and PaymentIntent details to client
        return jsonify({'publishableKey': STRIPE_PUBLISHABLE_KEY, 'clientSecret': intent.client_secret,
                        'intentId': intent.get('id')})
    except Exception as e:
        return jsonify(error=str(e)), 403


@app.route('/api/handle-payment')
def handle_payment():
    if email := auth.check_login(request):
        intent_id = request.args.get("intentId")

        if not intent_id:
            log_info("No intentId passed " + str(request.form))
            return api.serialize(False)

        intent = stripe.PaymentIntent.retrieve(intent_id)

        log_info("Amount Paid: " + str(intent['amount_received']) + " cents")

        if intent['amount_received'] >= intent['amount']:
            return api.serialize(api.pay_for_session(email, intent_id))

        return api.serialize(False)

    log_info("Not logged in")
    return ""

@app.route('/api/handle-payment-donation')
def handle_payment_donation():
    intent_id = request.args.get("intentId", None, str)
    name = request.args.get("name", "", str)
    log_info(str(intent_id) + str(name))

    if not intent_id:
        log_info("No intentId passed " + str(request.form))
        return api.serialize(False)

    intent = stripe.PaymentIntent.retrieve(intent_id)

    log_info("Amount Paid: " + str(intent['amount_received']) + " cents")

    if intent['amount_received'] >= intent['amount']:
        log_info("Sending Donation Email...")
        notify.Email().send("ethan.chapman@comcast.net", "New Donation",
                            "A new donation was just received"
                            "\n\nDonor Name: " + name +
                            "\nDonation Amount: " + str(intent['amount_received']) + " cents" +
                            "\nIntent ID: " + intent_id)
        log_info("Email Sent!")
        return api.serialize(True)

    return api.serialize(False)


@app.route('/api/handle-payment-discount')
def handle_payment_discount():
    if email := auth.check_login(request):
        code = request.args.get("discount-code")
        if auth.check_discount(code):  # will return true if it works
            return api.serialize(api.pay_for_session(email))

    return api.serialize(False)


if __name__ == '__main__':
    app.run()
