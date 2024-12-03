from manage_student import db
from manage_student.models import Student, Score, Subject, Semester, Class, Year, Students_Classes
from sqlalchemy.orm import aliased

# Hàm lấy tất cả các lớp học
def get_classes():
    try:
        classes = db.session.query(Class).all()
        if not classes:
            print("Không có lớp học trong cơ sở dữ liệu.")
        return classes
    except Exception as e:
        print(f"Lỗi khi truy vấn lớp học: {str(e)}")
        return []

# Hàm lấy tất cả các môn học
def get_subjects():
    try:
        return db.session.query(Subject).all()
    except Exception as e:
        print(f"Lỗi khi truy vấn môn học: {str(e)}")
        return []

# Hàm lấy tất cả các học kỳ
def get_semesters():
    try:
        semesters = db.session.query(Semester).all()
        if not semesters:
            print("Không có học kỳ trong cơ sở dữ liệu.")
        return semesters
    except Exception as e:
        print(f"Lỗi khi truy vấn học kỳ: {str(e)}")
        return []

# Hàm lấy tất cả các năm học
def get_years():
    try:
        return db.session.query(Year).all()
    except Exception as e:
        print(f"Lỗi khi truy vấn năm học: {str(e)}")
        return []

# Hàm lấy học sinh theo các bộ lọc (theo lớp, học kỳ, môn học, năm học)
def get_students_by_filter(class_id=None, semester_id=None, subject_id=None, year_id=None):
    query = db.session.query(Student)

    # Kết nối với bảng Students_Classes và Class
    if class_id:
        query = query.join(Students_Classes).join(Class).filter(Class.id == class_id)

    # Kết nối với bảng Score nếu cần lọc theo môn học, học kỳ và năm
    if semester_id or subject_id or year_id:
        score_alias = aliased(Score)  # Tạo bí danh cho bảng Score
        query = query.outerjoin(score_alias, Student.id == score_alias.student_id)

        if semester_id:
            query = query.filter(score_alias.semester_id == semester_id)
        if subject_id:
            query = query.filter(score_alias.subject_id == subject_id)
        if year_id:
            query = query.filter(score_alias.year_id == year_id)

    return query.all()

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def save_student_scores(student_id, score_15_min_list, score_1_hour_list, final_exam, subject_id, semester_id, year_id):
    try:
        score_15_min = [float(score) for score in score_15_min_list if score]
        score_1_hour = [float(score) for score in score_1_hour_list if score]
        final_exam = float(final_exam) if final_exam else 0.0

        logger.debug(f"Saving scores for student {student_id}: 15min={score_15_min}, 1 hour={score_1_hour}, final_exam={final_exam}")

        # Lưu điểm 15 phút
        for score in score_15_min:
            score_record = Score.query.filter_by(
                student_id=student_id,
                subject_id=subject_id,
                semester_id=semester_id,
                year_id=year_id,
                type='EXAM_15P'
            ).first()
            if score_record:
                logger.debug("Updating existing score record")
                score_record.score = score
            else:
                logger.debug("Creating new score record")
                new_score = Score(
                    student_id=student_id,
                    score=score,
                    type='EXAM_15P',
                    subject_id=subject_id,
                    semester_id=semester_id,
                    year_id=year_id
                )
                db.session.add(new_score)

        # Lưu điểm 1 giờ
        for score in score_1_hour:
            score_record = Score.query.filter_by(
                student_id=student_id,
                subject_id=subject_id,
                semester_id=semester_id,
                year_id=year_id,
                type='EXAM_45P'
            ).first()
            if score_record:
                logger.debug("Updating existing score record")
                score_record.score = score
            else:
                logger.debug("Creating new score record")
                new_score = Score(
                    student_id=student_id,
                    score=score,
                    type='EXAM_45P',
                    subject_id=subject_id,
                    semester_id=semester_id,
                    year_id=year_id
                )
                db.session.add(new_score)

        # Lưu điểm cuối kỳ
        score_record = Score.query.filter_by(
            student_id=student_id,
            subject_id=subject_id,
            semester_id=semester_id,
            year_id=year_id,
            type='EXAM_final'
        ).first()
        if score_record:
            logger.debug("Updating existing score record")
            score_record.score = final_exam
        else:
            logger.debug("Creating new score record")
            new_score = Score(
                student_id=student_id,
                score=final_exam,
                type='EXAM_final',
                subject_id=subject_id,
                semester_id=semester_id,
                year_id=year_id
            )
            db.session.add(new_score)

        db.session.commit()
        logger.debug("Scores saved successfully.")
        return "Lưu điểm thành công"

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving scores: {str(e)}")
        return f"Đã xảy ra lỗi: {str(e)}"
