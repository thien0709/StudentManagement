from flask import render_template, request, redirect, flash, url_for
from manage_student.dao import auth, score
from manage_student import app, login, admin, models
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
    # Lấy các tham số môn học, học kỳ, năm học từ request.form
    subject_id = request.form.get("subject_id")
    semester_id = request.form.get("semester_id")
    year_id = request.form.get("year_id")

    print(f"Subject ID: {subject_id}, Semester ID: {semester_id}, Year ID: {year_id}")  # Log các tham số

    try:
        # Lặp qua tất cả các điểm trong form
        for key, value in request.form.to_dict(flat=False).items():
            print(f"Key: {key}, Value: {value}")  # Log tất cả các dữ liệu nhận được từ form

            if key.startswith("score_15_min"):
                student_id = key.split("[")[1].split("]")[0]

                # Lấy các điểm từ form
                score_15_min = request.form.getlist(f"score_15_min[{student_id}]")
                score_1_hour = request.form.getlist(f"score_1_hour[{student_id}]")
                final_exam = request.form.get(f"final_exam[{student_id}]")

                print(f"Student ID: {student_id}, 15 min scores: {score_15_min}, 1 hour scores: {score_1_hour}, Final exam: {final_exam}")

                if subject_id and semester_id and year_id:
                    # Kiểm tra nếu điểm hợp lệ
                    try:
                        score_15_min = [float(score) for score in score_15_min if score.strip()]
                        score_1_hour = [float(score) for score in score_1_hour if score.strip()]
                        final_exam_score = float(final_exam) if final_exam else 0.0

                        # Tính toán tổng điểm và điểm trung bình
                        total_score_15_min = sum(score_15_min)  # Tổng điểm 15 phút
                        total_score_1_hour = sum(score_1_hour) * 2  # Trọng số 2 cho điểm 1 tiết
                        final_exam_score = final_exam_score if final_exam else 0.0

                        total_weight = len(score_15_min) + len(score_1_hour) * 2 + 3
                        average_score = (total_score_15_min + total_score_1_hour + final_exam_score * 3) / total_weight if total_weight else 0

                        # Lưu điểm vào cơ sở dữ liệu
                        Score.save_student_scores(student_id, score_15_min, score_1_hour, final_exam, subject_id, semester_id, year_id)

                        # Lưu điểm trung bình vào cơ sở dữ liệu
                        Score.save_average_score(student_id, round(average_score, 1))

                    except ValueError as ve:
                        flash(f"Điểm không hợp lệ cho học sinh {student_id}: {ve}", "error")
                        continue  # Tiếp tục nếu có lỗi điểm không hợp lệ

        flash("Lưu điểm thành công!", "success")  # Thêm thông báo flash
    except Exception as e:
        flash(f"Đã xảy ra lỗi: {str(e)}", "error")  # Thêm thông báo lỗi nếu có ngoại lệ

    return redirect(url_for("input_scores"))




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
    app.run(debug=True, port=9999)