from functools import wraps
from urllib import request
from flask import session, redirect, url_for, flash, jsonify
from flask_login import current_user



def require_role(roles):
    def wrap(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Vui lòng đăng nhập trước khi truy cập trang này.", "error")
                return redirect(url_for('login_process'))

            if current_user.role not in roles:
                flash("Bạn không có quyền truy cập vào trang này.", "error")
                return redirect(url_for('index'))

            return f(*args, **kwargs)

        return decorated_function
    return wrap