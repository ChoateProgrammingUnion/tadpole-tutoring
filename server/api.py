import database
import validators
import auth

# @app.route('/api/register')
def register_student(request):
    """
    Only for students, need to ensure that they have paid
    """
    email = auth.check_login(request)
    if email:
        db = database.Database()
        db.init_db_connection()
        db.add_student(email)
        db.end_db_connection()
        return True
    return False

# @app.route('/api/person')
def get_student(request, email: str):
    """
    Reserved for teachers, admins, or students searching themselves. Returns dict of the student's data
    """
    if validators.email(email) and email_requestor := auth.check_teacher(request) :
        if email_requestor and validators.email(email_requestor):
            db = database.Database()
            db.init_db_connection()
            student = db.get_student(email)
            db.end_db_connection()
        return student

    elif validators.email(email) and email_requestor := auth.check_login(request):
        if email_requestor and validators.email(email_requestor) and email == email_requestor:
            db = database.Database()
            db.init_db_connection()
            student = db.get_student(email)
            db.end_db_connection()

            if 'notes' in student:
                del student['notes']

            return student

    return {}



# @app.route('/api/teachers')
def fetch_teachers(request):
    """
    Gets all teachers
    Only for signed-in users
    """
    pass

def update_time(request):
    pass

def confirm_teacher(request):
    pass

def claim_teacher(request):
    pass

def claim_time(request):
    pass
