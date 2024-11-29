from flask import render_template, request, redirect
from manage_student.dao import auth
from manage_student import app,login
from flask_login import login_user, logout_user


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=['get', 'post'])
def login_process():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        u = auth.auth_user(username=username, password=password)
        if u:
            login_user(u)
            return redirect('/')
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')


@app.route("/logout", methods=['get', 'post'])
def logout_process():
    logout_user()
    return redirect("/login")


@login.user_loader
def load_user(user_id):
    return auth.get_user_by_id(user_id)


if __name__ == '__main__':
    app.run(debug=True, port=9999)
