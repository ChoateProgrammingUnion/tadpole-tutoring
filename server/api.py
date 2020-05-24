import database
import validators
import auth
import codecs
# import pickle
import json
import pytz

from datetime import datetime, timedelta

from notifications import notify
from utils.log import *


# @app.route('/api/register')
def register_student(request):
    """
    Only for students, need to ensure that they have paid
    """
    email = auth.check_login(request)
    if email:
        db = database.Database()
        db.add_student(email, "", "")
        return True
    return False

# @app.route('/api/person')
def get_person(request):
    """
    Reserved for teachers, admins, or students searching themselves. Returns dict of the student's data
    """

    email = request.args.get("email", None, str)
    # log_info("email is " + email)

    if not email:
        log_info("get_person was called, but no email was provided in request")
        return None

    if validators.email(email) and (email_requester := auth.check_teacher(request)):
        if email_requester and validators.email(email_requester):
            db = database.Database()
            student = db.get_student(email)
        return dict(student)

    elif validators.email(email) and (email_requester := auth.check_login(request)):
        if email_requester and validators.email(email_requester) and email == email_requester:
            db = database.Database()
            student = db.get_student(email)
            if 'notes' in student:
                del student['notes']

            return dict(student)

    log_info("No person with email " + email + " found in database")
    return None

# @app.route('/api/teachers')
def fetch_teachers(subject=None, available=True):
    db = database.Database()

    if available:
        midnight = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = midnight - timedelta(days=midnight.weekday())
        week_end = week_start + timedelta(days=7)

        return db.get_available_teachers(week_start, week_end, subject)
    else:
        return db.all_teachers(subject)

def update_time(request):
    id = request.args.get("id", None, int)
    start_time = request.args.get("start_time", None, int)
    duration_type = request.args.get("duration_type", None, int)
    claimed = request.args.get("claimed", None, bool)
    student = request.args.get("student", None, str)

    if id:
        db = database.Database()

        edited = db.edit_time(id, start_time, duration_type, claimed, student)
        return edited

    log_info("update_time was called, but no id was specified")
    return False

def pay_for_session(email, intent_id=None):
    db = database.Database()

    cart, intent = db.get_cart(email)
    if intent_id is None or intent_id == intent:
        log_info("Server cart matches intent cart, claiming times...")
        sender = notify.Email()
        email_times = [1, 12]
        times = []
        for t_id in cart:
            # email.send(teacher_email, "Tadpole Tutoring Payment Confirmation", "This is a confirmation that you have signed up for ")
            db.claim_time(email, t_id)
            # try:
            session = db.get_time_by_id(t_id)
            teacher = db.get_teacher(session['teacher_email'])
            time = datetime.fromtimestamp(int(session['start_time'])).astimezone(pytz.utc)
            times.append(time.strftime("%I:%M%p UTC on %B %d, %Y") + " With " + str(teacher['first_name']) + " " + str(teacher['last_name']) + " (" + str(teacher['email']) + ", " + str(teacher['zoom_id']) + ")")
            sender.send(session['teacher_email'], "Tadpole Tutoring Student Registration",
                        "Dear Tutor,\n\nA student has signed up for your class at " +
                        time.strftime("%I:%M%p UTC on %B %d, %Y") +
                        ".\nThe student's name is " + session['student'] +
                        ".\n\nThese times are in Universal Coordinated Time (UTC). To view these times in your local timezone, click the link below."
                        "\nhttps://tadpoletutoring.org/sessions.html\n\nFive minutes before the time of your scheduled session, open up your personal zoom meeting, "
                        "ensure your password is set to 0000, enable your waiting room, and be prepared to admit the student!!! "
                        "Congrats on your session!\n\nFrom, Tadpole Tutoring")


            for i in email_times:
                if time - timedelta(hours=i) < datetime.now().astimezone(pytz.utc) and i != 1:
                    continue
                db._insert("notifications", {
                    "email": {
                        "address": session['teacher_email'],
                        "subject": str(i) + " Hour Reminder: Tadpole Tutoring Session",
                        "msg": "Dear Tutor,\n\nThis is a reminder that a student has signed up for your class at " +
                               time.strftime("%I:%M%p UTC on %B %d, %Y") + ".\nThe student's name is " +
                               session['student'] +
                               ".\n\nFive minutes before the time of your scheduled session, open up your personal zoom meeting, "
                               "ensure your password is set to 0000, enable your waiting room, and be prepared to admit the student!!! "
                               "Congrats on your session! \n\nFrom, Tadpole Tutoring"
                    },
                    "sent": False,
                    "time": time - timedelta(hours=i)
                }
                           )
                zoom_id = str(teacher.get('zoom_id'))
                phone_number = str(teacher.get('phone_number'))
                if phone_number:
                    db._insert("notifications", {
                        "email": {
                            "address": email,
                            "subject": str(i) + " Hour Reminder: Tadpole Tutoring Session",
                            "msg": "Dear Student,\n\nThis is a reminder that you have signed up for a class at " +
                                   time.strftime("%I:%M%p UTC on %B %d, %Y") +
                                   ".\nThe teacher's email address is " + session['teacher_email'] +
                                   ".\n\n Zoom: " + zoom_id +
                                   "\n\nPhone Number: " + str(phone_number) +
                                   "\n\n\nPassword: 0000\n\n\nFrom, Tadpole Tutoring"
                        },
                        "sent": False,
                        "time": time - timedelta(hours=i)
                    }
                               )
                else:
                    db._insert("notifications", {
                        "email": {
                            "address": email,
                            "subject": str(i) + " Hour Reminder: Tadpole Tutoring Session",
                            "msg": "Dear Student,\n\nThis is a reminder that you have signed up for a class at " +
                                   time.strftime("%I:%M%p UTC on %B %d, %Y") +
                                   ".\nThe teacher's email address is " + session['teacher_email'] +
                                   ".\n\n Zoom: " + zoom_id +
                                   "\n\nPhone Number: " + str(phone_number) +
                                   "\n\n\nPassword: 0000\n\n\nFrom, Tadpole Tutoring"
                        },
                        "sent": False,
                        "time": time - timedelta(hours=i)
                    }
                               )
            # except Exception:
            #     log_info("EMAIL FAILED")


        db.set_cart(email, set())
        log_info("Times claimed")

        sender.send(email, "Tadpole Tutoring Payment Confirmation",
                    "Dear Student, \n\nThanks for scheduling a teaching session with us! This is a confirmation that you have signed up for " +
                    str(len(cart)) + " session(s) on the following dates:\n" + "\n".join(times) +
                    "\n\nThese times are in Universal Coordinated Time (UTC). To view these times in your local timezone, click the link below."
                    "\nhttps://tadpoletutoring.org/sessions.html\n\n\nFrom, Tadpole Tutoring")
        return True


def make_teacher(request):
    student_email = request.args.get("student_email", None, str)

    if student_email:
        db = database.Database()

        succeeded = db.make_teacher(student_email, [])
        return succeeded

    log_info("confirm_teacher was called, but no student email was specified")
    return False

def claim_time(request):
    student_email = request.args.get("student_email", None, str)
    time_id = request.args.get("time_id", None, int)

    if student_email and time_id:
        db = database.Database()

        succeeded = db.claim_time(student_email, time_id)
        return succeeded

    log_info("claim_time was called, student_email and time_id weren't specified")
    return False

def serialize(obj):
    return json.dumps(obj)
    # return codecs.encode(pickle.dumps(obj), "base64").decode()

def deserialize(obj_str):
    return json.loads(obj_str)
    # return pickle.loads(codecs.decode(obj_str.encode(), "base64"))