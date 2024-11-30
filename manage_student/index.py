from flask import render_template, request, flash, redirect, url_for

from manage_student import app, dao


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/input_scores", methods=["GET"])
def input_scores():
    classes = dao.get_classes()
    subjects = dao.get_subjects()
    semesters = dao.get_semesters()
    years = dao.get_years()

    # Lấy các tham số từ form (sử dụng request.args.get để lấy query params)
    class_id = request.args.get("class_id")
    semester_id = request.args.get("semester_id")
    subject_id = request.args.get("subject_id")
    year_id = request.args.get("year_id")


    students = []
    if class_id and semester_id and subject_id and year_id:
        students = dao.get_students_by_filter(class_id, semester_id, subject_id, year_id)


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
        for key, value in request.form.to_dict(flat=False).items():
            print(f"Key: {key}, Value: {value}")  # Log tất cả các dữ liệu nhận được từ form

            if key.startswith("score_15_min"):
                student_id = key.split("[")[1].split("]")[0]
                score_15_min = request.form.getlist(f"score_15_min[{student_id}]")
                score_1_hour = request.form.getlist(f"score_1_hour[{student_id}]")
                final_exam = request.form.get(f"final_exam[{student_id}]")

                print(f"Student ID: {student_id}, 15 min scores: {score_15_min}, 1 hour scores: {score_1_hour}, Final exam: {final_exam}")

                if subject_id and semester_id and year_id:
                    # Tính toán điểm trung bình
                    total_score_15_min = sum([float(score) for score in score_15_min])  # Tổng điểm 15 phút
                    total_score_1_hour = sum([float(score) for score in score_1_hour]) * 2  # Trọng số 2 cho điểm 1 tiết
                    final_exam_score = float(final_exam) if final_exam else 0.0

                    total_weight = len(score_15_min) + len(score_1_hour) * 2 + 3
                    average_score = (total_score_15_min + total_score_1_hour + final_exam_score * 3) / total_weight if total_weight else 0

                    # Lưu điểm vào cơ sở dữ liệu
                    dao.save_student_scores(student_id, score_15_min, score_1_hour, final_exam, subject_id, semester_id, year_id)

                    # Lưu điểm trung bình vào cơ sở dữ liệu
                    dao.save_average_score(student_id, round(average_score, 1))

        flash("Lưu điểm thành công!", "success")  # Thêm thông báo flash
    except Exception as e:
        flash(f"Đã xảy ra lỗi: {str(e)}", "error")  # Thêm thông báo lỗi nếu có ngoại lệ

    return redirect(url_for("routes.input_scores"))



if __name__ == "__main__":
    app.run(debug=True)
