import os
from datetime import datetime
from io import BytesIO
from flask import render_template, redirect, flash, url_for, current_app, session, jsonify
from manage_student.dao import auth_dao, score_dao, class_dao, subject_dao, semester_dao, year_dao, student_dao
from manage_student import app, login, models, admin
from flask_login import login_user, logout_user, current_user
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from manage_student import app, login, models, db, admin
from manage_student.dao import auth_dao
from manage_student.dao.class_dao import get_classes_by_grade
from manage_student.dao.grade_dao import api_get_grades, api_get_classes_by_grade, api_get_class_amount, \
    api_get_passed_count
from manage_student.dao.profile_dao import add_profile
from manage_student.dao.score_dao import count_students_passed
from manage_student.dao.score_dao import logger
from manage_student.dao.semester_dao import get_semesters, api_get_semesters
from manage_student.dao.subject_dao import get_subjects, api_get_subjects
from manage_student.dao.teaching_assignment_dao import  check_assignment
from manage_student.dao.year_dao import get_years, api_get_years
from manage_student.decorator import require_teacher_role
from manage_student.form import TeachingTaskForm
from manage_student.models import ExamType, Subject, Teacher, Class, Semester, Year, TeachingAssignment
from manage_student.models import Grade, Student, StudentClass, Score
from manage_student.dao.teaching_assignment_dao import check_assignment, get_all_assignments, add_teaching_assignment
from manage_student.decorator import require_teacher_role, role_only
from manage_student.form import TeachingTaskForm
from manage_student.models import ExamType, Subject, Teacher, Class, Semester, Year, TeachingAssignment, UserRole
# from manage_student.decorator import require_employee_role


@app.route("/")
def index():
    if current_user.is_authenticated:
        return render_template("index.html", username=current_user.username)
    return render_template("index.html")


from flask import redirect, url_for


from flask import Flask, request, jsonify, render_template, redirect, url_for
from datetime import datetime

@app.route("/studentForm", methods=["GET", "POST"])
def formStudent():
    if request.method == "POST":
        # Lấy dữ liệu từ form hoặc JSON
        if request.is_json:
            data = request.get_json()
            full_name = data.get("fullName")
            email = data.get("email")
            phone = data.get("phone")
            dob = data.get("dob")
            address = data.get("address")
            gender = data.get("gender")
        else:
            full_name = request.form.get("fullName")
            email = request.form.get("email")
            phone = request.form.get("phone")
            dob = request.form.get("dob")
            address = request.form.get("address")
            gender = request.form.get("gender")

        # Kiểm tra nếu thiếu thông tin
        if not all([full_name, email, phone, dob, address, gender]):
            return jsonify({"status": "error", "message": "Chưa đủ thông tin!"})

        # Kiểm tra tính hợp lệ của email
        import re
        email_pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.match(email_pattern, email):
            return jsonify({"status": "error", "message": "Email không hợp lệ!"})

        # Kiểm tra giới tính
        if gender not in ['male', 'female']:
            return jsonify({"status": "error", "message": "Giới tính không hợp lệ!"})

        # Chuyển đổi ngày sinh từ chuỗi
        try:
            dob = datetime.strptime(dob, "%Y-%m-%d")
        except ValueError:
            return jsonify({"status": "error", "message": "Ngày sinh không hợp lệ!"})

        # Thêm hồ sơ vào cơ sở dữ liệu
        try:
            add_profile(full_name, email, dob, gender, address, phone)
            # Trả về phản hồi thành công
            return jsonify({"status": "success", "message": "Hồ sơ đã được thêm thành công!"})
        except Exception as e:
            return jsonify({"status": "error", "message": f"Đã xảy ra lỗi: {str(e)}"})
    return render_template("student_form.html")




# Thong ke bao cao
@app.route("/chartscreen")
def reportChart():
    return render_template("chartScreen.html")


# Lay hoc ki
@app.route('/api/semesters', methods=['GET'])
def api_get_semesters_route():
    return api_get_semesters()



# Lay nam hoc

@app.route('/api/years', methods=['GET'])
def api_get_years_route():
    return api_get_years()

# Lay mon hoc

@app.route('/api/subjects', methods=['GET'])
def api_get_subjects_route():
    return api_get_subjects()


# Route lấy tất cả các khối (Grade)
@app.route('/get_grades', methods=['GET'])
def get_grades_route():
    return api_get_grades()

@app.route('/get_classes_by_grades', methods=['GET'])
def get_classes_route():
    grade = request.args.get('grade')  # Lấy tham số 'grade' từ query string
    if grade:
        return api_get_classes_by_grade(grade)
    else:
        return jsonify({"error": "Không có khối học được chọn"}), 400

# Route lấy sĩ số (số học sinh) theo lớp
@app.route('/get_class_amount/<class_id>', methods=['GET'])
def get_class_amount_route(class_id):
    return api_get_class_amount(class_id)

@app.route('/get_passed_count', methods=['GET'])
def get_passed_count_route():
    class_id = request.args.get('class_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    semester_id = request.args.get('semester_id', type=int)
    year_id = request.args.get('year_id', type=int)

    # Kiểm tra tham số đầu vào
    if not all([class_id, subject_id, semester_id, year_id]):
        return jsonify({'error': 'Missing or invalid parameters'}), 400

    return api_get_passed_count(class_id, subject_id, semester_id, year_id)


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

@app.route("/input_scores", methods=["GET", "POST"])
@require_teacher_role
def input_scores():
    # Chuyển hướng nếu người dùng không có quyền
    if session.get('role') != models.UserRole.TEACHER.value:
        return redirect(url_for('index'))

    # Lấy danh sách phân công giảng dạy của giáo viên
    teacher_id = current_user.id
    assignments = TeachingAssignment.query.filter_by(teacher_id=teacher_id).all()

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
    average_scores = {}

    if request.method == "POST":
        class_id = int(request.form.get("class_id"))
        semester_id = int(request.form.get("semester_id"))
        subject_id = int(request.form.get("subject_id"))
        year_id = int(request.form.get("year_id"))

        # Kiểm tra phân công giảng dạy
        if not check_assignment(assignments, class_id, subject_id, semester_id, year_id):
            return redirect(url_for('input_scores', error="Bạn không được phân công giảng dạy lớp học này. ",
                                    info="Bạn có muốn xem <a href='{{ url_for('teaching_assignments') }}'>danh sách lớp học mà bạn được phân công</a>?"))

        try:
            # Lưu điểm
            students = student_dao.get_students_by_filter(class_id, semester_id, subject_id, year_id)
            for student in students:
                student_id = student.id
                scores_15_min = request.form.getlist(f"score_15_min_{student_id}[]")
                scores_1_hour = request.form.getlist(f"score_1_hour_{student_id}[]")
                final_exam = request.form.get(f"final_exam_{student_id}")

                score_dao.save_student_scores(
                    student_id, scores_15_min, scores_1_hour, final_exam, subject_id, semester_id, year_id
                )

            flash("Lưu điểm thành công!", "success")

            # Redirect lại với các query parameters để tránh load mất dữ liệu
            return redirect(url_for("input_scores", class_id=class_id, semester_id=semester_id, subject_id=subject_id,
                                    year_id=year_id))

        except Exception as e:
            flash(f"Đã xảy ra lỗi: {str(e)}", "error")

    # GET request: Hiển thị danh sách sinh viên và điểm
    if class_id and semester_id and subject_id and year_id:
        class_id = int(class_id)
        semester_id = int(semester_id)
        subject_id = int(subject_id)
        year_id = int(year_id)

        # Kiểm tra phân công
        if not check_assignment(assignments, class_id, subject_id, semester_id, year_id):
            return redirect(url_for('input_scores', error="Bạn không được phân công giảng dạy lớp học này. ",
                                    info="Bạn có muốn xem <a href='{{ url_for('teaching_assignments') }}'>danh sách lớp học mà bạn được phân công</a>?"))

        students = student_dao.get_students_by_filter(class_id, semester_id, subject_id, year_id)
        scores_data = score_dao.get_scores_by_filter(semester_id, subject_id, year_id)

        for score in scores_data:
            student_id = str(score.student_id)
            exam_type = score.exam_type.name

            if student_id not in scores:
                scores[student_id] = {"score_15_min": [], "score_1_hour": [], "final_exam": None}

            if exam_type == "EXAM_15P":
                scores[student_id]["score_15_min"].append(score.score)
            elif exam_type == "EXAM_45P":
                scores[student_id]["score_1_hour"].append(score.score)
            elif exam_type == "EXAM_FINAL":
                scores[student_id]["final_exam"] = score.score

        # Tính điểm trung bình
        student_ids = [student.id for student in students]
        average_scores = score_dao.calculate_average_scores(student_ids, semester_id, subject_id, year_id)

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
        average_scores=average_scores,
    )

@app.route("/export", methods=["GET"])
@require_teacher_role
def export():
    # Lấy danh sách phân công giảng dạy của giáo viên
    teacher_id = current_user.id
    assignments = TeachingAssignment.query.filter_by(teacher_id=teacher_id).all()

    classes = class_dao.get_classes()
    subjects = subject_dao.get_subjects()
    years = year_dao.get_years()

    # Tạo dictionary ánh xạ ID lớp với tên lớp
    classes_dict = {class_.id: class_.name for class_ in classes}

    class_id = request.args.get("class_id")
    subject_id = request.args.get("subject_id")
    year_id = request.args.get("year_id")

    students = []
    average_scores = {}

    if class_id and subject_id and year_id:
        class_id = int(class_id)
        subject_id = int(subject_id)
        year_id = int(year_id)

        # Kiểm tra phân công giảng dạy (cho cả 2 học kỳ)
        if not check_assignment(assignments, class_id, subject_id, 1, year_id) and not check_assignment(assignments, class_id, subject_id, 2, year_id):
            flash("Bạn không được phân công giảng dạy lớp học này.", "error")
            return redirect(url_for('input_scores'))

        # Sử dụng hàm get_students_by_filter để lấy danh sách học sinh
        students = student_dao.get_students_by_filter(class_id=class_id, subject_id=subject_id, year_id=year_id)

        print("classes_dict:", classes_dict)  # In ra classes_dict
        # In ra danh sách học sinh và class_id (đã sửa)
        for student in students:
            for student_class in student.classes:
                print(f"Student {student.name()} - Class ID: {student_class.class_id}")

        # Tính điểm trung bình cho từng học kỳ
        for semester_id in [1, 2]:
            student_ids = [student.id for student in students]
            semester_avg_scores = score_dao.calculate_average_scores(student_ids, semester_id, subject_id, year_id)
            for student_id, avg_score in semester_avg_scores.items():
                if student_id not in average_scores:
                    average_scores[student_id] = {}
                average_scores[student_id][semester_id] = avg_score

    return render_template(
        "export.html",
        classes=classes,
        subjects=subjects,
        years=years,
        students=students,
        class_id=class_id,
        subject_id=subject_id,
        year_id=year_id,
        average_scores=average_scores,
        classes_dict=classes_dict  # Truyền dictionary vào template
    )


from flask import send_file, request
import pandas as pd
from manage_student.dao import class_dao, semester_dao, subject_dao, year_dao, student_dao, score_dao


@app.route('/export_scores', methods=['GET'])
@require_teacher_role
def export_scores():
    # Chuyển hướng nếu người dùng không có quyền
    if session.get('role') != models.UserRole.TEACHER.value:
        return redirect(url_for('index'))

    # Lấy danh sách phân công giảng dạy của giáo viên
    teacher_id = current_user.id
    assignments = TeachingAssignment.query.filter_by(teacher_id=teacher_id).all()

    try:
        class_id = int(request.args.get("class_id"))
        semester_id = int(request.args.get("semester_id"))
        subject_id = int(request.args.get("subject_id"))
        year_id = int(request.args.get("year_id"))

        # Kiểm tra phân công giảng dạy
        if not check_assignment(assignments, class_id, subject_id, semester_id, year_id):
            flash("Bạn không được phân công giảng dạy lớp học này.", "error")
            return redirect(url_for('input_scores'))

        class_name = class_dao.get_class_name(class_id)
        semester_name = semester_dao.get_semester_name(semester_id)
        subject_name = subject_dao.get_subject_name(subject_id)
        years = year_dao.get_years()

        logger.debug(
            f"Export Scores: class_id={class_id}, semester_id={semester_id}, subject_id={subject_id}, year_id={year_id}")

        excel_data = {}

        for year in years:
            year_id = year.id
            year_name = year.name

            students = student_dao.get_students_by_filter(class_id, semester_id, subject_id, year_id)
            scores_data = score_dao.get_scores_by_filter(semester_id, subject_id, year_id)

            scores_dict = {}
            for score in scores_data:
                student_id = str(score.student_id)
                if student_id not in scores_dict:
                    scores_dict[student_id] = {"score_15_min": [], "score_1_hour": [], "final_exam": None}

                if score.exam_type == ExamType.EXAM_15P:
                    scores_dict[student_id]["score_15_min"].append(score.score)
                elif score.exam_type == ExamType.EXAM_45P:
                    scores_dict[student_id]["score_1_hour"].append(score.score)
                elif score.exam_type == ExamType.EXAM_FINAL:
                    scores_dict[student_id]["final_exam"] = score.score

            data = []
            for student in students:
                student_scores = scores_dict.get(str(student.id), {})
                student_id_int = int(student.id)

                avg_scores = score_dao.calculate_average_scores([student_id_int], semester_id, subject_id, year_id)
                logger.debug(f"Calculated avg_scores: {avg_scores}")
                avg_score = avg_scores.get(student_id_int, 0)
                logger.debug(
                    f"Calculating average score for student {student.profile.name} ({student_id_int}): {avg_score}")

                row = {
                    "Tên sinh viên": student.name(),
                    "Điểm 15 phút": ", ".join(f"{score:.1f}" for score in student_scores.get("score_15_min", [])),
                    "Điểm 1 tiết": ", ".join(f"{score:.1f}" for score in student_scores.get("score_1_hour", [])),
                    "Điểm thi cuối kỳ": f"{student_scores.get('final_exam', 0):.1f}",
                    "Điểm trung bình": f"{avg_score:.2f}",
                }

                logger.debug(f"Row data for student {student.id}: {row}")
                data.append(row)

            df = pd.DataFrame(data)

            excel_data[year_name] = {
                "dataframe": df,
                "class_name": class_name,
                "semester_name": semester_name,
                "subject_name": subject_name
            }

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for year_name, content in excel_data.items():
                df = content["dataframe"]
                class_name = content["class_name"]
                semester_name = content["semester_name"]
                subject_name = content["subject_name"]

                df.to_excel(writer, sheet_name=year_name, startrow=4, index=False)

                worksheet = writer.sheets[year_name]
                worksheet.write(0, 0, f"Lớp: {class_name}")
                worksheet.write(1, 0, f"Học kỳ: {semester_name}")
                worksheet.write(2, 0, f"Môn học: {subject_name}")

                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(4, col_num, value)

                # Định dạng tiêu đề và bảng
                header_format = writer.book.add_format(
                    {'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(4, col_num, value, header_format)

        output.seek(0)
        return send_file(output, as_attachment=True, download_name="student_scores.xlsx",
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    except Exception as e:
        logger.error(f"Error exporting scores: {str(e)}")
        return f"Đã xảy ra lỗi: {str(e)}"


@app.route('/export_pdf', methods=['GET'])
def export_pdf():
    # Chuyển hướng nếu người dùng không có quyền
    if session.get('role') != models.UserRole.TEACHER.value:
        return redirect(url_for('index'))

    # Lấy danh sách phân công giảng dạy của giáo viên
    teacher_id = current_user.id
    assignments = TeachingAssignment.query.filter_by(teacher_id=teacher_id).all()

    try:
        class_id = int(request.args.get("class_id"))
        semester_id = int(request.args.get("semester_id"))
        subject_id = int(request.args.get("subject_id"))
        year_id = int(request.args.get("year_id"))

        # Kiểm tra phân công giảng dạy
        if not check_assignment(assignments, class_id, subject_id, semester_id, year_id):
            flash("Bạn không được phân công giảng dạy lớp học này.", "error")
            return redirect(url_for('input_scores'))

        # Đăng ký font hỗ trợ tiếng Việt
        font_path = os.path.join(current_app.root_path, "templates/fonts/Roboto/Roboto-Regular.ttf")
        pdfmetrics.registerFont(TTFont('Roboto', font_path))

        styles = getSampleStyleSheet()
        styles['Normal'].fontName = 'Roboto'
        styles['Title'].fontName = 'Roboto'
        styles['Heading2'].fontName = 'Roboto'

        # Lấy thông tin dữ liệu
        class_name = class_dao.get_class_name(class_id)
        semester_name = semester_dao.get_semester_name(semester_id)
        subject_name = subject_dao.get_subject_name(subject_id)
        years = year_dao.get_years()

        pdf_data = []
        style_normal = styles['Normal']
        style_heading = styles['Heading2']

        for year in years:
            year_id = year.id
            year_name = year.name

            students = student_dao.get_students_by_filter(class_id, semester_id, subject_id, year_id)
            scores_data = score_dao.get_scores_by_filter(semester_id, subject_id, year_id)

            scores_dict = {}
            for score in scores_data:
                student_id = str(score.student_id)
                if student_id not in scores_dict:
                    scores_dict[student_id] = {"score_15_min": [], "score_1_hour": [], "final_exam": None}

                if score.exam_type == ExamType.EXAM_15P:
                    scores_dict[student_id]["score_15_min"].append(score.score)
                elif score.exam_type == ExamType.EXAM_45P:
                    scores_dict[student_id]["score_1_hour"].append(score.score)
                elif score.exam_type == ExamType.EXAM_FINAL:
                    scores_dict[student_id]["final_exam"] = score.score

            data = []
            for student in students:
                student_scores = scores_dict.get(str(student.id), {})
                student_id_int = int(student.id)

                avg_scores = score_dao.calculate_average_scores([student_id_int], semester_id, subject_id, year_id)
                avg_score = avg_scores.get(student_id_int, 0)

                row = [
                    student.name(),
                    ", ".join(f"{score:.1f}" for score in student_scores.get("score_15_min", [])),
                    ", ".join(f"{score:.1f}" for score in student_scores.get("score_1_hour", [])),
                    f"{student_scores.get('final_exam', 0):.1f}",
                    f"{avg_score:.2f}",
                ]
                data.append(row)

            pdf_data.append(Spacer(1, 12))
            pdf_data.append(Paragraph(f"Năm học: {year_name}", style_heading))
            pdf_data.append(Paragraph(f"Lớp: {class_name}", style_normal))
            pdf_data.append(Paragraph(f"Học kỳ: {semester_name}", style_normal))
            pdf_data.append(Paragraph(f"Môn học: {subject_name}", style_normal))
            pdf_data.append(Spacer(1, 12))

            # Tạo bảng với tiêu đề
            table_data = [
                             ["Tên sinh viên", "Điểm 15 phút", "Điểm 1 tiết", "Điểm thi cuối kỳ", "Điểm trung bình"]
                         ] + data

            table = Table(table_data, colWidths=[100, 100, 100, 100, 100])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Roboto'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            pdf_data.append(table)
            pdf_data.append(Spacer(1, 12))

        output = BytesIO()
        doc = SimpleDocTemplate(output, pagesize=A4)
        doc.build(pdf_data)

        output.seek(0)
        return send_file(output, as_attachment=True, download_name="student_scores.pdf", mimetype='application/pdf')

    except Exception as e:
        logger.error(f"Error exporting PDF: {str(e)}")
        return f"Đã xảy ra lỗi: {str(e)}"


@app.route("/class")
@role_only([UserRole.STAFF])
def edit_class():
    class_id = request.args.get('lop_hoc_id')
    year_id = request.args.get('nam_hoc_id')

    students_without_class = student_dao.get_students_without_class()
    # Kiểm tra nếu không có đủ thông tin, thông báo lỗi và redirect
    if not class_id or not year_id:
        error_message = "Vui lòng chọn đầy đủ lớp, học kỳ và năm học!"
        return render_template('staff/edit_class.html',
                               classes_list=class_dao.get_classes(),
                               semesters=semester_dao.get_semesters(),
                               years=year_dao.get_years(),
                               students=None,
                               students_without_class=students_without_class,
                               error_message=error_message,
                               selected_class_id=class_id,
                               selected_year_id=year_id)

    # Lấy danh sách học sinh theo bộ lọc lớp, học kỳ và năm học
    students = student_dao.get_students_by_class(class_id, year_id)
    for x in students:
        print(x.name())
    students_without_class = student_dao.get_students_without_class()
    return render_template('staff/edit_class.html',
                           classes_list=class_dao.get_classes(),
                           semesters=semester_dao.get_semesters(),
                           students_without_class=students_without_class,
                           years=year_dao.get_years(),
                           students=students,
                           selected_class_id=class_id,
                           selected_year_id=year_id)


@app.route('/assign_to_class', methods=['POST'])
def assign_to_class():
    class_dao.assign_students_to_classes()
    return redirect(url_for('edit_class'))

@app.route("/edit_student/<int:student_id>", methods=['GET', 'POST'])
def edit_student(student_id):
    student = student_dao.get_student_by_id(student_id)

    if not student and student_id != 0:
        return "Học sinh không tồn tại"

    if request.method == 'POST':
        action = request.form.get('action')
        class_id = request.form.get('lop_hoc')
        semester_id = request.form.get('hoc_ky')
        year_id = request.form.get('nam_hoc')
        print("test", class_id, semester_id, year_id)

        if action == 'edit':
            print("edit")
            name = request.form.get('ten_hoc_sinh')
            email = request.form.get('email')
            birthday = request.form.get('ngay_sinh')
            gender_str = request.form.get('gioi_tinh')
            gender = int(gender_str) if gender_str else 0
            address = request.form.get('dia_chi')
            phone = request.form.get('so_dien_thoai')

            updated_student = student_dao.update_student(
                student_id, name, email, birthday, gender, address, phone
            )

            if updated_student:
                students = student_dao.get_students_by_class(class_id, year_id)
                return redirect(url_for('edit_class', lop_hoc_id=class_id, hoc_ky_id=semester_id, nam_hoc_id=year_id))
            else:
                return "Lỗi cập nhật học sinh", 400

        elif action == 'delete':
            print("delete")
            student_dao.remove_student_from_class(student_id,class_id)
            students = student_dao.get_students_by_class(class_id, year_id)
            return redirect(url_for('edit_class', lop_hoc_id=class_id, hoc_ky_id=semester_id, nam_hoc_id=year_id))

        elif action == 'add':
            print("add")
            # Thêm học sinh mới
            name = request.form.get('ten_hoc_sinh')
            email = request.form.get('email')
            birthday = request.form.get('ngay_sinh')
            gender_str = request.form.get('gioi_tinh')
            gender = 1 if gender_str == 'Nam' else 0
            address = request.form.get('dia_chi')
            phone = request.form.get('so_dien_thoai')
            class_id = request.form.get('lop_hoc')

            student_dao.add_student(name, email, birthday, gender, address, phone, class_id, 'K12')

            # Lấy lại danh sách học sinh sau khi thêm
            students = student_dao.get_students_by_class(class_id, year_id)
            return redirect(url_for('edit_class', lop_hoc_id=class_id, hoc_ky_id=semester_id, nam_hoc_id=year_id))

        elif action == 'add_to_class':
            print("add_to_class")
            class_id = request.form.get('lop_hoc')
            student_dao.add_student_to_class(student_id, class_id)
            students = student_dao.get_students_by_class(class_id, year_id)
            return redirect(url_for('edit_class', lop_hoc_id=class_id, hoc_ky_id=semester_id, nam_hoc_id=year_id))

    # Render giao diện khi request là GET
    # students = student_dao.get_students_by_class(class_id, semester_id, year_id)
    return redirect(url_for('edit_class', lop_hoc_id=class_id, hoc_ky_id=semester_id, nam_hoc_id=year_id))


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

@app.route('/assign', methods=['GET', 'POST'])
def assign_task():
    form = TeachingTaskForm()

    # Tạo danh sách lựa chọn cho form
    form.teacher.choices = [(teacher.id, teacher.name()) for teacher in Teacher.query.all()]
    form.subject.choices = [(subject.id, subject.name) for subject in Subject.query.all()]
    form.classroom.choices = [(classroom.id, classroom.name) for classroom in Class.query.all()]
    form.semester.choices = [(semester.id, semester.name) for semester in Semester.query.all()]
    form.year.choices = [(year.id, year.name) for year in Year.query.all()]

    # Lấy danh sách phân công từ database thông qua DAO
    assignments_info = get_all_assignments()

    # Xử lý khi form được submit
    if form.validate_on_submit():
        teacher_id = form.teacher.data
        subjects_id = form.subject.data
        class_id = form.classroom.data
        semester_id = form.semester.data
        years_id = form.year.data
        # Thêm phân công mới vào database thông qua DAO
        new_assignment = add_teaching_assignment(
            teacher_id, subjects_id, class_id, semester_id, years_id
        )

        flash('Teaching assignment has been saved successfully!', 'success')
        return redirect(url_for('assign_task'))

    return render_template('/staff/teaching_assignment.html', form=form, assignments=assignments_info)


@app.route('/teaching_assignments')
@require_teacher_role
def teaching_assignments():
    teacher_id = current_user.id
    assignments = TeachingAssignment.query.filter_by(teacher_id=teacher_id).all()
    # Tạo list chứa các dictionary, mỗi dictionary chứa thông tin về một phân công
    assignments_info = []
    for assignment in assignments:
        class_name = Class.query.get(assignment.class_id).name
        subject_name = Subject.query.get(assignment.subjects_id).name
        semester_name = Semester.query.get(assignment.semester_id).name
        year_name = Year.query.get(assignment.years_id).name
        assignments_info.append({
            'class_name': class_name,
            'subject_name': subject_name,
            'semester_name': semester_name,
            'year_name': year_name
        })
    return render_template('staff/teaching_assignment.html', assignments=assignments_info)


@app.route("/check_assignment")
@require_teacher_role
def check_assignment_route():
    teacher_id = current_user.id
    assignments = TeachingAssignment.query.filter_by(teacher_id=teacher_id).all()
    class_id = int(request.args.get("class_id"))
    subject_id = int(request.args.get("subject_id"))
    semester_id = int(request.args.get("semester_id"))
    year_id = int(request.args.get("year_id"))
    assigned = check_assignment(assignments, class_id, subject_id, semester_id, year_id)
    return jsonify({'assigned': assigned})


@app.route("/login", methods=['get', 'post'])
def login_process():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        u = auth_dao.auth_user(username=username, password=password)
        if u:
            login_user(u)

            session['role'] = u.role.value

            # Chuyển hướng dựa trên vai trò
            if u.role == models.UserRole.ADMIN:
                return redirect('/admin')
            elif u.role == models.UserRole.TEACHER:
                return redirect('/input_scores')
            else:
                return redirect('/class')
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
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        avatar = request.files.get('avatar')
        role = request.form.get('role')

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

            login_user(new_user)

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
