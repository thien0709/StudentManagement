from flask import render_template, request, redirect
from manage_student.dao import auth
from manage_student import app, login, admin,models
from flask_login import login_user, logout_user, current_user


@app.route("/")
def index():
    if current_user.is_authenticated:
        return render_template("index.html", username=current_user.username)
    return render_template("index.html")


@app.route("/login", methods=['get', 'post'])
def login_process():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        u = auth.auth_user(username=username, password=password)
        if u:
            login_user(u)
            if u.user_role == models.UserRole.ADMIN:
                return redirect('/admin')
            else:
                return redirect('/')
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')


@app.route("/logout", methods=['get', 'post'])
def logout_process():
    logout_user()
    return redirect("/login")

@app.route("/register", methods=['GET', 'POST'])
def register_process():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            return render_template('register.html', error="Mật khẩu không khớp")
        existing_user = auth.get_user_by_username(username)
        if existing_user:
            return render_template('register.html', error="Tên đăng nhập đã tồn tại")

        success = auth.create_user(username=username, email=email, password=password)
        if success:
            return redirect('/login')
        else:
            return render_template('register.html', error="Có lỗi xảy ra, vui lòng thử lại sau")

    return render_template('register.html')

@login.user_loader
def load_user(user_id):
    return auth.get_user_by_id(user_id)




if __name__ == '__main__':
    app.run(debug=True, port=9999)
