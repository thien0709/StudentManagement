from app.models import db, Student, Score, Subject, Semester, Class, Year
from sqlalchemy.orm import aliased


# Hàm lấy tất cả các lớp
def get_classes():
    return db.session.query(Class).all()


# Hàm lấy tất cả các môn học
def get_subjects():
    return db.session.query(Subject).all()


# Hàm lấy tất cả các học kỳ
def get_semesters():
    return db.session.query(Semester).all()


# Hàm lấy tất cả các năm học
def get_years():
    return db.session.query(Year).all()


# Hàm lấy học sinh theo các bộ lọc (theo lớp, học kỳ, môn học, năm học)
def get_students_by_filter(class_id=None, semester_id=None, subject_id=None, year=None):
    query = db.session.query(Student)

    # Lọc theo lớp học nếu có
    if class_id:
        query = query.filter(Student.class_id == class_id)

    # Lọc theo học kỳ, môn học và năm học nếu có
    if semester_id or subject_id or year:
        score_alias = aliased(Score)  # Tạo bí danh cho bảng Score
        query = query.join(score_alias, Student.id == score_alias.student_id)

        # Lọc theo các tiêu chí
        if semester_id:
            query = query.filter(score_alias.semester_id == semester_id)
        if subject_id:
            query = query.filter(score_alias.subject_id == subject_id)
        if year:
            query = query.filter(score_alias.year_id == year)

    return query.all()


def save_student_scores(student_id, score_15_min_list, score_1_hour_list, final_exam, subject_id, semester_id, year_id):
    try:
        # Kiểm tra và chuyển đổi điểm
        score_15_min = [float(score) for score in score_15_min_list if score]
        score_1_hour = [float(score) for score in score_1_hour_list if score]
        final_exam = float(final_exam) if final_exam else 0.0

        print(f"Saving scores for student {student_id}: 15min={score_15_min}, 1 hour={score_1_hour}, final_exam={final_exam}")

        # Tìm bản ghi Score của học sinh theo các tham số (student_id, subject_id, semester_id, year_id)
        score_record = Score.query.filter_by(
            student_id=student_id,
            subject_id=subject_id,
            semester_id=semester_id,
            year_id=year_id
        ).first()

        if score_record:
            # Nếu có bản ghi, cập nhật lại các điểm
            score_record.score_15_min = ",".join([str(s) for s in score_15_min])
            score_record.score_1_hour = ",".join([str(s) for s in score_1_hour])
            score_record.final_exam = final_exam
        else:
            # Nếu không có bản ghi, tạo bản ghi mới
            new_score = Score(
                student_id=student_id,
                score_15_min=",".join([str(s) for s in score_15_min]),
                score_1_hour=",".join([str(s) for s in score_1_hour]),
                final_exam=final_exam,
                subject_id=subject_id,
                semester_id=semester_id,
                year_id=year_id
            )
            db.session.add(new_score)

        db.session.commit()  # Lưu dữ liệu vào cơ sở dữ liệu
        print("Scores saved successfully.")
        return "Lưu điểm thành công"

    except Exception as e:
        db.session.rollback()  # Hủy bỏ giao dịch nếu có lỗi
        print(f"Error saving scores: {str(e)}")
        return f"Đã xảy ra lỗi: {str(e)}"


# Hàm lưu điểm trung bình vào cơ sở dữ liệu
def save_average_score(student_id, average_score):
    try:
        # Tìm bản ghi Score của học sinh theo student_id
        score_record = Score.query.filter_by(student_id=student_id).first()

        if score_record:
            # Cập nhật điểm trung bình nếu đã có bản ghi
            score_record.average_score = average_score
            db.session.commit()
        else:
            # Nếu không có bản ghi nào, tạo mới
            new_score = Score(student_id=student_id, average_score=average_score)
            db.session.add(new_score)
            db.session.commit()

        return "Lưu điểm trung bình thành công"

    except Exception as e:
        db.session.rollback()  # Hủy bỏ giao dịch nếu có lỗi
        return f"Đã xảy ra lỗi khi lưu điểm trung bình: {str(e)}"
