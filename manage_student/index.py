from flask import render_template, request, redirect, flash, url_for
from manage_student.dao import auth_dao, score_dao, class_dao, subject_dao, semester_dao, year_dao, student_dao
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
    classes = class_dao.get_classes()  # Danh sách lớp
    subjects = subject_dao.get_subjects()  # Danh sách môn học
    semesters = semester_dao.get_semesters()  # Danh sách học kỳ
    years = year_dao.get_years()  # Danh sách năm học

    # Lấy các tham số từ URL query string (query params)
    class_id = request.args.get("class_id")
    semester_id = request.args.get("semester_id")
    subject_id = request.args.get("subject_id")
    year_id = request.args.get("year_id")
    # Kiểm tra nếu tất cả các tham số đã được cung cấp, tìm danh sách học sinh theo bộ lọc
    students = []
    if class_id and semester_id and subject_id and year_id:
        students = student_dao.get_students_by_filter(class_id, semester_id, subject_id, year_id)

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
                score_dao.save_student_scores(student_id, [score_15_min], [score_1_hour], final_exam, subject_id, semester_id, year_id)
    except Exception as e:
        flash(f"Đã xảy ra lỗi: {str(e)}", "error")

    return redirect(url_for('input_scores', class_id=class_id, semester_id=semester_id, subject_id=subject_id, year_id=year_id))


@app.route("/class", methods=['GET', 'POST'])
def edit_class():
    if request.method == 'GET':
        classes_list = class_dao.get_classes()
        semesters = semester_dao.get_semesters()
        years = year_dao.get_years()
        return render_template('staff/edit_class.html',
                               classes_list=classes_list,
                               semesters=semesters,
                               years=years,
                               students=None)

    elif request.method == 'POST':
        class_id = request.form.get('lop_hoc_id')
        semester_id = request.form.get('hoc_ky_id')
        year_id = request.form.get('nam_hoc_id')

        if not class_id or not semester_id or not year_id:
            error_message = "Vui lòng chọn đầy đủ lớp, học kỳ và năm học!"
            return render_template('staff/edit_class.html',
                                   classes_list=class_dao.get_classes(),
                                   semesters=semester_dao.get_semesters(),
                                   years=year_dao.get_years(),
                                   students=None,
                                   error_message=error_message)

        students = student_dao.get_students_by_class(class_id, semester_id, year_id)
        for student in students:
            print(student.profile.name)
            print(student.profile.birthday)
        return render_template('staff/edit_class.html',
                               classes_list=class_dao.get_classes(),
                               semesters=semester_dao.get_semesters(),
                               years=year_dao.get_years(),
                               students=students)


@app.route("/edit_student/<int:student_id>", methods=['GET', 'POST'])
def edit_student(student_id):
    student = student_dao.get_student_by_id(student_id)

    if not student and student_id != 0:
        return "Học sinh không tồn tại", 404

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'edit':
            # Lấy thông tin từ form để chỉnh sửa
            name = request.form.get('ten_hoc_sinh')
            email = request.form.get('email')
            birthday = request.form.get('ngay_sinh')
            gender_str = request.form.get('gioi_tinh')
            gender = 1 if gender_str == 'Nam' else 0
            address = request.form.get('dia_chi')
            phone = request.form.get('so_dien_thoai')

            updated_student = student_dao.update_student(
                student_id, name, email, birthday, gender, address, phone
            )

            if updated_student:
                return redirect('/class')
            else:
                return "Lỗi cập nhật học sinh", 400

        elif action == 'delete':
            student_dao.delete_student(student_id)
            return redirect('/class')

        elif action == 'add':
            # Lấy thông tin thêm học sinh
            name = request.form.get('ten_hoc_sinh')
            email = request.form.get('email')
            birthday = request.form.get('ngay_sinh')
            gender_str = request.form.get('gioi_tinh')
            gender = 1 if gender_str == 'Nam' else 0
            address = request.form.get('dia_chi')
            phone = request.form.get('so_dien_thoai')
            class_id = request.form.get('lop_hoc')  # Lớp học từ form

            # Thêm học sinh mới
            student_dao.add_student(name, email, birthday, gender, address, phone, class_id, 'K12')

    return render_template('edit_class.html', student=student)


# @app.route("/delete_student/<int:student_id>", methods=['POST'])
# def delete_student(student_id):
#     success = student_dao.delete_student(student_id)
#
#     if success:
#         return redirect('/students')
#     else:
#         return "Không tìm thấy học sinh", 404

@app.route("/login", methods=['get', 'post'])
def login_process():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        u = auth_dao.auth_user(username=username, password=password)
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
    return auth_dao.get_user_by_id(user_id)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
