import database
from utils.log import *


def check_login(request) -> str:
    """
    Returns email if logged in, if not return False.
    """
    token = request.cookies.get('token')
    email = request.cookies.get('email')

    authentication = database.Database()
    authentication.init_db_connection()
    if authentication.check_auth_pair(token, email):
        authentication.end_db_connection()
        log_info("Successfully checked cookie login for " + email)
        return email
    else:
        authentication.end_db_connection()
        log_info("Unsuccessfully checked cookie login for " + str(email))
        return False


def deauth_token(request):
    """
    Overwrites token
    """
    email = check_login(request)

    if email:
        log_info("Deauthed cookie login for " + str(email))
        authentication = database.Database()
        authentication.init_db_connection()
        authentication.create_token(email)
        authentication.end_db_connection()
    else:
        log_info("Deauthed cookie login failed for " + str(email))


def set_login(response, user_info) -> str:
    """
    Here, we assume that users are already authenticated. We create
    a new token regardless if one already exists.
    """
    if user_info and (email := user_info.get('email')) and user_info.get('email_verified') == "true":
        response.set_cookie('email', email)

        authentication = database.Database()
        authentication.init_db_connection()
        token = authentication.create_token(str(email))
        authentication.end_db_connection()
        response.set_cookie('token', token)

        log_info("Set login for " + email)
        return response

    log_info("Set login failed for " + str(email))
    return response

def check_teacher(request):
    email = check_login(request)
    if email:
        authentication = database.Database()
        return authentication.check_teacher(email)
    return False

