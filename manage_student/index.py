from flask import render_template, request, redirect, flash, url_for
from manage_student.dao import auth_dao, score_dao, class_dao, subject_dao, semester_dao, year_dao, student_dao
from manage_student import app, login, models , admin
from flask_login import login_user, logout_user, current_user

# from manage_student.decorator import require_employee_role
from manage_student.models import Subject


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

@app.route("/class")
# @require_employee_role
def edit_class():
    # Lấy dữ liệu từ GET thay vì POST
    class_id = request.args.get('lop_hoc_id')
    semester_id = request.args.get('hoc_ky_id')
    year_id = request.args.get('nam_hoc_id')

    # Kiểm tra nếu không có đủ thông tin, thông báo lỗi và redirect
    if not class_id or not semester_id or not year_id:
        error_message = "Vui lòng chọn đầy đủ lớp, học kỳ và năm học!"
        return render_template('staff/edit_class.html',
                               classes_list=class_dao.get_classes(),
                               semesters=semester_dao.get_semesters(),
                               years=year_dao.get_years(),
                               students=None,
                               error_message=error_message,
                               selected_class_id=class_id,
                               selected_semester_id=semester_id,
                               selected_year_id=year_id)

    # Lấy danh sách học sinh theo bộ lọc lớp, học kỳ và năm học
    students = student_dao.get_students_by_class(class_id, semester_id, year_id)

    return render_template('staff/edit_class.html',
                           classes_list=class_dao.get_classes(),
                           semesters=semester_dao.get_semesters(),
                           years=year_dao.get_years(),
                           students=students,
                           selected_class_id=class_id,
                           selected_semester_id=semester_id,
                           selected_year_id=year_id)


@app.route("/edit_student/<int:student_id>", methods=['GET', 'POST'])
# @require_employee_role
def edit_student(student_id):
    student = student_dao.get_student_by_id(student_id)

    if not student and student_id != 0:
        return "Học sinh không tồn tại"

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'edit':
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

            # Redirect về trang class sau khi thêm học sinh
            return redirect('/class')

    return render_template('edit_class.html', student=student)


# @app.route("/delete_student/<int:student_id>", methods=['POST'])
# def delete_student(student_id):
#     success = student_dao.delete_student(student_id)
#
#     if success:
#         return redirect('/students')
#     else:
#         return "Không tìm thấy học sinh", 404


# @app.route("/edit_subject", methods=['GET', 'POST'])
# def edit_subject():
#     if request.method == 'GET':
#         # This renders the edit form when the user first visits the page
#         return render_template('admin/subject.html')
#
#     elif request.method == 'POST':
#         # Here you would process the data from the form submitted (e.g., save changes to the database)
#         subject_name = request.form.get('subject_name')
#         subject_code = request.form.get('subject_code')
#         # More processing logic here, such as updating the subject in your database
#
#         # After processing, you may want to redirect or render a different template
#         return redirect(url_for('subject_list'))  # Or another page after successful POST

@app.route("/login", methods=['get', 'post'])
def login_process():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        u = auth_dao.auth_user(username=username, password=password)
        if u:
            login_user(u)
            if u.role == models.UserRole.ADMIN:
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

@app.route("/register", methods=['GET', 'POST'])
def register_process():
    if request.method == 'POST':
        name = request.form.get('name')  # Retrieve the name from the form
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        avatar = request.files.get('avatar')
        role = request.form.get('role')  # Retrieve the selected role

        # Validate passwords
        if password != confirm_password:
            return render_template('register.html', error='Mật khẩu và xác nhận mật khẩu không khớp',
                                   username=username, email=email)

        # Validate role
        if role not in ['staff', 'teacher']:
            return render_template('register.html', error='Vai trò không hợp lệ',
                                   username=username, email=email)

        # Map role string to UserRole enum
        role_enum = models.UserRole.STAFF if role == 'staff' else models.UserRole.TEACHER

        # Check if username already exists
        existing_user = auth_dao.get_user_by_username(username)
        if existing_user:
            return render_template('register.html', error='Tên người dùng đã tồn tại',
                                   username=username, email=email)

        # Pass name to the add_user function
        new_user = auth_dao.add_user(username=username, email=email, password=password, role=role_enum, avatar=avatar,
                                     name=name)

        if new_user:
            # Automatically log in the user
            login_user(new_user)

            # Redirect to appropriate page based on role
            if new_user.role == models.UserRole.ADMIN:
                return redirect('/admin')
            else:
                return redirect('/')

        else:
            return render_template('register.html', error='Đã có lỗi xảy ra khi đăng ký.',
                                   username=username, email=email)

    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
