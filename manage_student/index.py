from flask import render_template, request, redirect, flash, url_for
from manage_student.dao import auth, score
from manage_student import app, login, admin, models, db
from flask_login import login_user, logout_user, current_user

from manage_student.models import Score


@app.route("/")
def index():
    if current_user.is_authenticated:
        return render_template("index.html", username=current_user.username)

    return render_template("index.html")


@app.route("/input_scores", methods=["GET"])
def input_scores():
    # Lấy dữ liệu từ các hàm trong model 'score'
    classes = score.get_classes()  # Danh sách lớp
    subjects = score.get_subjects()  # Danh sách môn học
    semesters = score.get_semesters()  # Danh sách học kỳ
    years = score.get_years()  # Danh sách năm học

    # In ra các giá trị để kiểm tra dữ liệu
    print(f"Classes: {classes}")
    print(f"Subjects: {subjects}")
    print(f"Semesters: {semesters}")
    print(f"Years: {years}")

    # Lấy các tham số từ URL query string (query params)
    class_id = request.args.get("class_id")
    semester_id = request.args.get("semester_id")
    subject_id = request.args.get("subject_id")
    year_id = request.args.get("year_id")

    # In ra các tham số từ query string để kiểm tra
    print(f"class_id: {class_id}, semester_id: {semester_id}, subject_id: {subject_id}, year_id: {year_id}")

    # Kiểm tra nếu tất cả các tham số đã được cung cấp, tìm danh sách học sinh theo bộ lọc
    students = []
    if class_id and semester_id and subject_id and year_id:
        students = score.get_students_by_filter(class_id, semester_id, subject_id, year_id)

    # Trả về template với các dữ liệu đã lấy được
    return render_template(
        "input_scores.html",
        classes=classes,
        subjects=subjects,
        semesters=semesters,
        years=years,
        students=students,
        class_id=class_id,
        semester_id=semester_id,
        subject_id=subject_id,
        year_id=year_id
    )


@app.route("/save-scores", methods=["POST"])
def save_scores():
    class_id = request.form.get("class_id")
    semester_id = request.form.get("semester_id")
    subject_id = request.form.get("subject_id")
    year_id = request.form.get("year_id")
    try:
        for key, value in request.form.to_dict(flat=False).items():
            if key.startswith("score_15_min"):
                student_id = key.split("_")[3]
                score_15_min = request.form.get(f"score_15_min_{student_id}")
                score_1_hour = request.form.get(f"score_1_hour_{student_id}")
                final_exam = request.form.get(f"final_exam_{student_id}")

                if not all([score_15_min, score_1_hour, final_exam]):
                    print(f"Error: Missing score for student {student_id}")
                    continue
                score.save_student_scores(student_id, [score_15_min], [score_1_hour], final_exam, subject_id, semester_id, year_id)
    except Exception as e:
        flash(f"Đã xảy ra lỗi: {str(e)}", "error")

    return redirect(url_for('input_scores', class_id=class_id, semester_id=semester_id, subject_id=subject_id, year_id=year_id))


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


@login.user_loader
def load_user(user_id):
    return auth.get_user_by_id(user_id)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
