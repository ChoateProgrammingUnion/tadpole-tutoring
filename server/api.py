import database
import validators
import auth
import codecs
# import pickle
import json

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
def fetch_teachers(subject):
    db = database.Database()

    if subject is not None:
        all_teachers = db.all_teachers(subject)
    else:
        all_teachers = db.all_teachers()
    return all_teachers

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