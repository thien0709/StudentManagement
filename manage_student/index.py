from flask import render_template, request, redirect, flash, url_for, session
from manage_student.dao import auth_dao, score_dao, class_dao, subject_dao, semester_dao, year_dao, student_dao
from manage_student import app, login, admin, models, db
from flask_login import login_user, logout_user, current_user
from flask import session

from manage_student.models import Score


@app.route("/")
def index():
    if current_user.is_authenticated:
        return render_template("index.html", username=current_user.username)

    return render_template("index.html")


@app.route("/input_scores", methods=["GET"])
def input_scores():
    classes = class_dao.get_classes()
    subjects = subject_dao.get_subjects()
    semesters = semester_dao.get_semesters()
    years = year_dao.get_years()

    class_id = request.args.get("class_id")
    semester_id = request.args.get("semester_id")
    subject_id = request.args.get("subject_id")
    year_id = request.args.get("year_id")

    students = []
    scores = {}  # Khởi tạo scores ở đây để tránh lỗi nếu không có đủ tham số
    if class_id and semester_id and subject_id and year_id:
        students = student_dao.get_students_by_filter(class_id, semester_id, subject_id, year_id)

        # Lấy điểm từ database và lưu vào session
        scores_data = score_dao.get_scores_by_filter(semester_id, subject_id, year_id)  # Loại bỏ class_id

        # Chuyển đổi scores_data sang định dạng phù hợp với template
        for score in scores_data:
            student_id = str(score.student_id)
            exam_type = score.exam_type.name
            if student_id not in scores:
                scores[student_id] = {
                    "score_15_min": [],
                    "score_1_hour": [],
                    "final_exam": None
                }
            if exam_type == "EXAM_15P":
                scores[student_id]["score_15_min"].append(score.score)
            elif exam_type == "EXAM_45P":
                scores[student_id]["score_1_hour"].append(score.score)
            elif exam_type == "EXAM_FINAL":
                scores[student_id]["final_exam"] = score.score

        session['scores'] = scores

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
        year_id=year_id,
        scores=scores  # Sử dụng biến scores đã được khởi tạo
    )

@app.route("/save-scores", methods=["POST"])
def save_scores():
    class_id = request.form.get("class_id")
    semester_id = request.form.get("semester_id")
    subject_id = request.form.get("subject_id")
    year_id = request.form.get("year_id")

    try:
        students = student_dao.get_students_by_filter(class_id, semester_id, subject_id, year_id)

        for student in students:
            student_id = student.id
            scores_15_min = request.form.getlist(f"score_15_min_{student_id}[]")
            scores_1_hour = request.form.getlist(f"score_1_hour_{student_id}[]")
            final_exam = float(request.form.get(f"final_exam_{student_id}"))

            # Lưu điểm vào database (sử dụng ScoreDAO)
            score_dao.save_student_scores(
                student_id,
                [float(score) for score in scores_15_min],
                [float(score) for score in scores_1_hour],
                final_exam,
                subject_id,
                semester_id,
                year_id
            )

            # Cập nhật session['scores']
            session['scores'][str(student_id)] = {
                "score_15_min": scores_15_min,
                "score_1_hour": scores_1_hour,
                "final_exam": final_exam
            }

        flash("Lưu điểm thành công!", "success")


        return redirect(url_for('input_scores',
                                class_id=class_id,
                                semester_id=semester_id,
                                subject_id=subject_id,
                                year_id=year_id))

    except Exception as e:
        db.session.rollback()
        flash(f"Đã xảy ra lỗi: {str(e)}", "error")
        return redirect(request.url)

    # @app.route("/class", methods=['GET', 'POST'])
# def edit_class():
#     if request.method == 'GET':
#         # Hiển thị danh sách lớp, học kỳ, và năm học
#         classes_list = class_dao.get_classes()
#         semesters = score.get_semesters()
#         years = score.get_years()
#         return render_template('staff/edit_class.html',
#                                classes_list=classes_list,
#                                semesters=semesters,
#                                years=years,
#                                students=None)
#
#     elif request.method == 'POST':
#         # Lấy dữ liệu từ form
#         class_id = request.form.get('class_id')
#         semester_id = request.form.get('semester_id')
#         year_id = request.form.get('year_id')
#
#         # # Kiểm tra xem người dùng có điền đủ thông tin không
#         # if not class_id or not semester_id or not year_id:
#         #     error_message = "Vui lòng chọn đầy đủ lớp, học kỳ và năm học!"
#         #     return render_template('staff/edit_class.html',
#         #                            classes_list=classes.get_classes(),
#         #                            semesters=score.get_semesters(),
#         #                            years=score.get_years(),
#         #                            students=None,
#         #                            error_message=error_message)
#
#         # Lấy danh sách học sinh nếu có đầy đủ thông tin
#         students = class_dao.get_students_by_class(class_id, semester_id, year_id)
#         return render_template('staff/edit_class.html',
#                                classes_list=class_dao.get_classes(),
#                                semesters=score.get_semesters(),
#                                years=score.get_years(),
#                                students=students)

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
