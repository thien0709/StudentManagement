from functools import wraps
from urllib import request
from flask import session, redirect, url_for, flash, jsonify
from flask_login import current_user

from manage_student.models import UserRole

def require_employee_role(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Kiểm tra đã đăng nhập chưa
        if 'role' not in session:
            return jsonify({
                "status": "error",
                "message": "Vui lòng đăng nhập trước khi truy cập trang này."
            }), 401  # 401 Unauthorized

        # Kiểm tra xem người dùng có vai trò STAFF hay không
        if session['role'] != UserRole.STAFF:
            return jsonify({
                "status": "error",
                "message": "Bạn không có quyền vào trang này."
            }), 403  # 403 Forbidden

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
                return redirect(url_for('index', msg = "Bạn không có quyền truy cập vào trang này."))
            else:
                return f(*args, **kwargs)
        return decorated_function
    return wrap