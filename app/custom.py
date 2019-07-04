from flask import abort
from flask_login import current_user
from functools import wraps

def require_role(roles=["User"]):
    def wrap(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if current_user.is_authenticated:
                if current_user.has_roles(roles):
                    return func(*args, **kwargs)
            return abort(401)
        return decorated_view
    return wrap