from flask import render_template, request, redirect, url_for, jsonify, flash, session
from flask_login import login_user, logout_user, current_user

from dao.semester_dao import get_semesters
from dao.subject_dao import get_subjects
from dao.year_dao import get_years
from manage_student import app, login, models, db
from manage_student.dao import auth_dao, score_dao, class_dao, subject_dao, semester_dao, year_dao, student_dao
from manage_student.dao.class_dao import get_classes_by_grade
from manage_student.dao.profile_dao import add_profile
from manage_student.dao.score_dao import count_students_passed, logger
from manage_student.models import Class, Grade, Student, StudentClass, Score, ExamType


@app.route("/")
def index():
    if current_user.is_authenticated:
        return render_template("index.html", username=current_user.username)

    return render_template("index.html")


# Route: form
@app.route("/studentForm", methods=["GET", "POST"])
def formStudent():
    if request.method == "POST":
        # Lấy dữ liệu từ form
        full_name = request.form.get("fullName")
        email = request.form.get("email")
        phone = request.form.get("phone")
        dob = request.form.get("dob")
        address = request.form.get("address")
        gender = request.form.get("gender")

        # Kiểm tra nếu thiếu thông tin
        if not all([full_name, email, phone, dob, address, gender]):
            return jsonify({"status": "error", "message": "Chưa đủ thông tin!"})

        # Nếu tất cả thông tin có đủ, tạo profile và lưu vào cơ sở dữ liệu
        result = add_profile(full_name, email, dob, gender, address, phone)

        if result == True:
            # Trả về phản hồi thành công
            return jsonify({"status": "success", "message": "Thông tin đã được lưu thành công!"})
            return redirect(url_for('index'))
        else:
            # Nếu có lỗi, trả về phản hồi lỗi
            return jsonify(result)
    return render_template("student_form.html")


# Thong ke bao cao
@app.route("/chartscreen")
def reportChart():
    return render_template("chartScreen.html")


# Lay hoc ki
@app.route('/api/semesters', methods=['GET'])
def api_get_semesters():
    try:
        semesters = get_semesters()
        semester_list = [{'id': s.id, 'name': s.name} for s in semesters]
        return jsonify({'semesters': semester_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Lay nam hoc
@app.route('/api/years', methods=['GET'])
def api_get_years():
    try:
        years = get_years()
        year_list = [{'id': y.id, 'name': y.name} for y in years]
        return jsonify({'years': year_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Lay mon hoc
@app.route('/api/subjects', methods=['GET'])
def api_get_subjects():
    try:
        subjects = get_subjects()
        subject_list = [{'id': s.id, 'name': s.name} for s in subjects]
        return jsonify({'subjects': subject_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Route lấy tất cả các khối (Grade)
@app.route('/get_grades', methods=['GET'])
def get_grades():
    try:
        grades = [grade.name for grade in Grade]
        return jsonify(grades)
    except Exception as e:
        return jsonify({"error": f"Lỗi khi lấy khối: {str(e)}"}), 500


# Lay si so class va grade
@app.route('/get_classes_by_grades', methods=['GET'])
def get_classes():
    grade = request.args.get('grade')  # Lấy tham số 'grade' từ query string
    if grade:
        classes = get_classes_by_grade(grade)
        class_data = [{"id": c.id, "name": c.name} for c in classes]
        return jsonify(class_data)
    else:
        return jsonify({"error": "Không có khối học được chọn"}), 400


# Route lấy sĩ số (số học sinh) theo lớp
@app.route('/get_class_amount/<class_id>', methods=['GET'])
def get_class_amount(class_id):
    try:
        class_data = db.session.query(Class).get(class_id)
        if class_data:
            return jsonify({"amount": class_data.amount})
        else:
            return jsonify({"error": "Không tìm thấy lớp"}), 404
    except Exception as e:
        return jsonify({"error": f"Lỗi khi lấy sĩ số: {str(e)}"}), 500


# Route lấy sĩ số đạt (điểm trung bình >= 5)
@app.route('/get_passed_count', methods=['GET'])
def get_passed_count():
    # Lấy các tham số từ request
    class_id = request.args.get('class_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    semester_id = request.args.get('semester_id', type=int)
    year_id = request.args.get('year_id', type=int)

    # Kiểm tra tham số đầu vào
    if not all([class_id, subject_id, semester_id, year_id]):
        return jsonify({'error': 'Missing or invalid parameters'}), 400

    try:
        # Đếm số học sinh đạt yêu cầu
        passed_count = count_students_passed(class_id, subject_id, semester_id, year_id)
        return jsonify({'passed_count': passed_count})
    except Exception as e:
        logger.error(f"Error in /get_passed_count: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# route tính điểm trung bình của các loại điểm trong môn học để vẽ chart
@app.route('/api/average_scores', methods=['GET'])
def get_average_scores():
    class_id = request.args.get('class_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    semester_id = request.args.get('semester_id', type=int)
    year_id = request.args.get('year_id', type=int)

    try:
        # Lấy danh sách học sinh
        student_ids = db.session.query(Student.id).join(StudentClass).filter(StudentClass.class_id == class_id).all()
        student_ids = [s[0] for s in student_ids]

        if not student_ids:
            return jsonify({"error": "No students found"}), 404

        # Lấy điểm từ bảng `Score`
        scores = Score.query.filter(
            Score.student_id.in_(student_ids),
            Score.subject_id == subject_id,
            Score.semester_id == semester_id,
            Score.year_id == year_id
        ).all()

        # Tính trung bình từng loại điểm
        def calculate_average(exam_type):
            exam_scores = [score.score for score in scores if score.exam_type == exam_type]
            return round(sum(exam_scores) / len(exam_scores), 2) if exam_scores else 0

        avg_15_min = calculate_average(ExamType.EXAM_15P)
        avg_1_hour = calculate_average(ExamType.EXAM_45P)
        avg_final = calculate_average(ExamType.EXAM_FINAL)

        return jsonify({
            "average_15_min": avg_15_min,
            "average_1_hour": avg_1_hour,
            "average_final": avg_final
        })

    except Exception as e:
        logger.error(f"Error fetching average scores: {str(e)}")
        return jsonify({"error": str(e)}), 500


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
    scores = {}
    if class_id and semester_id and subject_id and year_id:
        students = student_dao.get_students_by_filter(class_id, semester_id, subject_id, year_id)

        # Lấy điểm từ database và lưu vào session
        scores_data = score_dao.get_scores_by_filter(semester_id, subject_id, year_id)

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
        scores=scores,
        average_scores=session.get('average_scores', {})  # Truyền biến average_scores vào template

    )


@app.route("/save-scores", methods=["POST"])
def save_scores():
    class_id = request.form.get("class_id")
    semester_id = request.form.get("semester_id")
    subject_id = request.form.get("subject_id")
    year_id = request.form.get("year_id")

    try:
        students = student_dao.get_students_by_filter(class_id, semester_id, subject_id, year_id)
        session['average_scores'] = {}  # Khởi tạo biến mới trong session

        for student in students:
            student_id = student.id
            scores_15_min = request.form.getlist(f"score_15_min_{student_id}[]")
            scores_1_hour = request.form.getlist(f"score_1_hour_{student_id}[]")
            final_exam = float(request.form.get(f"final_exam_{student_id}"))

            # Tính toán điểm trung bình
            average_score = calculate_average_score(scores_15_min, scores_1_hour, final_exam)
            # Cập nhật session['average_scores']
            session['average_scores'][str(student.id)] = average_score

            # Cập nhật session['scores'] TRƯỚC KHI LƯU VÀO DATABASE
            session['scores'][str(student.id)] = {
                "score_15_min": scores_15_min,
                "score_1_hour": scores_1_hour,
                "final_exam": final_exam,
                "average_score": average_score
            }

            # Lưu điểm vào database
            score_dao.save_student_scores(
                student_id,
                [float(score) for score in scores_15_min],
                [float(score) for score in scores_1_hour],
                final_exam,
                subject_id,
                semester_id,
                year_id
            )

        flash("Lưu điểm thành công!", "success")
        return redirect(url_for('input_scores',
                                class_id=class_id,
                                semester_id=semester_id,
                                subject_id=subject_id,
                                year_id=year_id), code=303)

    except Exception as e:
        db.session.rollback()
        flash(f"Đã xảy ra lỗi: {str(e)}", "error")
        return redirect(request.url)


def calculate_average_score(scores_15_min, scores_1_hour, final_exam):
    score_15_min = sum([float(score) for score in scores_15_min])
    score_1_hour = sum([float(score) for score in scores_1_hour])
    total_weight = len(scores_15_min) * 1 + len(scores_1_hour) * 2 + 3
    average_score = (score_15_min + score_1_hour * 2 + final_exam * 3) / total_weight
    return round(average_score, 2)


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
