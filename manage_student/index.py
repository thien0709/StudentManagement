import os

from flask import render_template, request, redirect, flash, url_for, current_app, session, jsonify
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from io import BytesIO

from semester import assignments

from manage_student.dao import auth_dao, score_dao, class_dao, subject_dao, semester_dao, year_dao, student_dao
from manage_student import app, login, models , admin
from flask_login import login_user, logout_user, current_user
from manage_student.dao.score_dao import logger
from manage_student.decorator import require_teacher_role
from manage_student.form import TeachingTaskForm
from manage_student.models import ExamType, Subject, Teacher, Class, Semester, Year, TeachingAssignment


# from manage_student.decorator import require_employee_role

# Hàm kiểm tra phân công giảng dạy
def check_assignment(assignments, class_id, subject_id, semester_id, year_id):
    """Kiểm tra xem giáo viên có được phân công giảng dạy
       môn học, lớp học, học kỳ và năm học tương ứng hay không.
    """
    for assignment in assignments:
        if (assignment.class_id == class_id and
            assignment.subjects_id == subject_id and
            assignment.semester_id == semester_id and
            assignment.years_id == year_id):
            return True
    return False


@app.route("/")
def index():
    if current_user.is_authenticated:
        return render_template("index.html", username=current_user.username)
    return render_template("index.html")

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
            return redirect(url_for("input_scores", class_id=class_id, semester_id=semester_id, subject_id=subject_id, year_id=year_id))

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

        logger.debug(f"Export Scores: class_id={class_id}, semester_id={semester_id}, subject_id={subject_id}, year_id={year_id}")

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
                logger.debug(f"Calculating average score for student {student.profile.name} ({student_id_int}): {avg_score}")

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
                header_format = writer.book.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(4, col_num, value, header_format)

        output.seek(0)
        return send_file(output, as_attachment=True, download_name="student_scores.xlsx", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

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
# @require_employee_role
def edit_class():

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





# Trong view, truyền dữ liệu
@app.route('/assign', methods=['GET', 'POST'])
def assign_task():
    form = TeachingTaskForm()
    form.teacher.choices = [(teacher.id, teacher.name()) for teacher in Teacher.query.all()]
    form.subject.choices = [(subject.id, subject.name) for subject in Subject.query.all()]
    form.classroom.choices = [(classroom.id, classroom.name) for classroom in Class.query.all()]
    form.semester.choices = [(semester.id, semester.name) for semester in Semester.query.all()]
    form.year.choices = [(year.id, year.name) for year in Year.query.all()]

    if form.validate_on_submit():
        # Xử lý form sau khi submit
        pass

    return render_template('/staff/teaching_assignment.html', form=form)


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