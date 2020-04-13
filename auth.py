import secrets
import string
from typing import Union, Tuple, Any

import dataset
import oauthlib
import validators as validators
from flask import session
from flask_dance.contrib.google import google

from config import *
import database
from utils.log import *
import cognito

def check_login(request) -> str:
    """
    Returns email if logged in, if not return False.
    """
    token = request.cookies.get('token')
    email = request.cookies.get('email')

    authentication = database.Database()
    if authentication.check_auth_pair(token, email):
        log_info("Successfully checked cookie login for " + email)
        return email
    else:
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
        authentication.create_token(email)
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
        token = authentication.create_token(str(email))
        response.set_cookie('token', token)

        log_info("Set login for " + email)
        return response

    log_info("Set login failed for " + str(email))
    return response


