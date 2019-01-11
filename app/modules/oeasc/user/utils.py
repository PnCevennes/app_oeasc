from functools import wraps
from pypnusershub import routes as fnauth
from flask import request


def check_auth_redirect_login(level):
    '''
        use fnauth.check_auth to check user auth
        if not auth redirect to the login page with the requested url as request argument
    '''
    def _check_auth_redirect_login(f):
        @wraps(f)
        def __check_auth_redirect_login(*args, **kwargs):
            redirect_url = 'user/login?redirect="' + request.url + '"'
            return fnauth.check_auth(level, False, redirect_url)(f)(*args, **kwargs)
        return __check_auth_redirect_login
    return _check_auth_redirect_login
