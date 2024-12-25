from functools import wraps
from urllib import request
from flask import session, redirect, url_for, flash
from flask_login import current_user

from manage_student.models import UserRole

def require_employee_role(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Kiểm tra đã đăng nhập chưa
        if 'role' not in session:
            flash("Vui lòng đăng nhập trước khi truy cập trang này.", "error")
            return redirect(url_for('login_process'))  # Nếu chưa đăng nhập, redirect về login

        # Kiểm tra xem người dùng có vai trò STAFF hay không
        if session['role'] != UserRole.STAFF:
            flash("Bạn không có quyền truy cập vào trang này.", "error")
            return redirect(url_for('home'))  # Nếu không có quyền, redirect về trang home

        return f(*args, **kwargs)

    return decorated_function



def require_teacher_role(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Kiểm tra đã đăng nhập chưa
        if not current_user.is_authenticated:
            flash("Vui lòng đăng nhập trước khi truy cập trang này.", "error")
            return redirect(url_for('login_process'))

        # Kiểm tra xem người dùng có vai trò TEACHER hay không
        if session.get('role') != UserRole.TEACHER.value:
            flash("Bạn không có quyền truy cập vào trang này.", "error")
            return redirect(url_for('index'))

        return f(*args, **kwargs)

    return decorated_function

def role_only(role):
    def wrap(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Vui lòng đăng nhập trước khi truy cập trang này.", "error")
                return redirect(url_for('login_process'))
            if current_user.role not in role:
                flash("Quyền không phù hợp", "forbidden")
                return redirect(url_for('index'))
            else:
                return f(*args, **kwargs)
        return decorated_function
    return wrap