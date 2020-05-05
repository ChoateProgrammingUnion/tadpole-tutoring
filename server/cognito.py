import json
import config
from config import AUTH_URL
import requests
import base64

def check_callback(request) -> dict:
    """
    Returns user info object (dict)
    Keys in dict:
        email: str
        email_verified: bool
        sub: UUID?
        username: str
    """
    code = str(request.args.get('code'))
    print("token", code, "request", request.args)
    tokens = exchange_code(code)

    user_info = get_user_info(tokens)

    return user_info

def exchange_code(code: str) -> dict:
    """
    Exchanges a code for an access token as per:
        https://docs.aws.amazon.com/cognito/latest/developerguide/token-endpoint.html
    """
    authorization = "Basic " + base64.b64encode(str(config.APP_CLIENT_ID + ":" + config.APP_CLIENT_SECRET).encode()).decode()

    headers = {"Authorization": authorization,
               "Content-Type": "application/x-www-form-urlencoded"}
    params = {"grant_type": "authorization_code", 
              "client_id": config.APP_CLIENT_ID, 
              "code" : code, 
              "redirect_uri" : "http://api.tadpoletutoring.org/callback"} 

    response = requests.post(AUTH_URL, 
                             params=params,
                             headers=headers
                            )

    if response.status_code == 200:
        return json.loads(response.content)
    else:
        raise ValueError("oauth not working!") # add some more logging in this case

def get_user_info(token: dict) -> dict:
    """
    Returns a JSON object from the token as per:
        https://docs.aws.amazon.com/cognito/latest/developerguide/userinfo-endpoint.html
    """
    headers = {"Authorization": "Bearer " + str(token.get("access_token"))} 
    response = requests.get("https://register.tadpoletutoring.org/oauth2/userInfo", headers=headers)

    if response.status_code == 200:
        return json.loads(response.content)
    else:
        raise ValueError("oauth not working!") # add some more logging in this case

def get_login_url():
    if "127.0.0.1" in config.SERVER_NAME:
        config.SERVER_NAME = config.SERVER_NAME.replace("127.0.0.1", "localhost")
    if "localhost" in config.SERVER_NAME:
        url = "https://register.tadpoletutoring.org/login?client_id=" + config.APP_CLIENT_ID + "&response_type=code&scope=aws.cognito.signin.user.admin+email+openid+phone+profile&redirect_uri=http://" + config.SERVER_NAME + "/callback"
        print(url)
    else:
        url = "https://register.tadpoletutoring.org/login?client_id=" + config.APP_CLIENT_ID + "&response_type=code&scope=aws.cognito.signin.user.admin+email+openid+phone+profile&redirect_uri=https://" + config.SERVER_NAME + "/callback"
        print(url)
    return url


