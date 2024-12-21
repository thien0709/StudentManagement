import logging

from manage_student import db
from manage_student.models import Score, ExamType, Student, StudentClass

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
                exam_type='EXAM_15P'
            ).first()
            if score_record:
                logger.debug("Updating existing score record")
                score_record.score = score
            else:
                logger.debug("Creating new score record")
                new_score = Score(
                    student_id=student_id,
                    score=score,
                    exam_type='EXAM_15P',
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
                exam_type='EXAM_45P'
            ).first()
            if score_record:
                logger.debug("Updating existing score record")
                score_record.score = score
            else:
                logger.debug("Creating new score record")
                new_score = Score(
                    student_id=student_id,
                    score=score,
                    exam_type='EXAM_45P',
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
            exam_type='EXAM_final'
        ).first()
        if score_record:
            logger.debug("Updating existing score record")
            score_record.score = final_exam
        else:
            logger.debug("Creating new score record")
            new_score = Score(
                student_id=student_id,
                score=final_exam,
                exam_type='EXAM_final',
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


def calculate_average_scores(student_ids, semester_id=None, subject_id=None, year_id=None):
    average_scores = {}
    for student_id in student_ids:
        query = Score.query.filter_by(student_id=student_id)
        if semester_id:
            query = query.filter_by(semester_id=semester_id)
        if subject_id:
            query = query.filter_by(subject_id=subject_id)
        if year_id:
            query = query.filter_by(year_id=year_id)
        scores = query.all()

        # Phân loại điểm và trọng số
        score_15_min = sum([score.score for score in scores if score.exam_type == ExamType.EXAM_15P]) or 0
        score_1_hour = sum([score.score for score in scores if score.exam_type == ExamType.EXAM_45P]) or 0
        final_exam = next((score.score for score in scores if score.exam_type == ExamType.EXAM_FINAL), 0)

        weight_15_min = len([score for score in scores if score.exam_type == ExamType.EXAM_15P])
        weight_1_hour = len([score for score in scores if score.exam_type == ExamType.EXAM_45P]) * 2
        weight_final = 3 if any(score.exam_type == ExamType.EXAM_FINAL for score in scores) else 0
        total_weight = weight_15_min + weight_1_hour + weight_final

        # Tính điểm trung bình
        if total_weight == 0:
            average_score = 0
        else:
            average_score = (score_15_min + score_1_hour * 2 + final_exam * 3) / total_weight

        # Lưu kết quả
        average_scores[student_id] = round(average_score, 2)

    return average_scores


def count_students_passed(class_id, subject_id, semester_id, year_id):
    try:
        # Lấy danh sách học sinh trong lớp cụ thể thông qua bảng trung gian StudentClass
        student_ids = db.session.query(Student.id).join(StudentClass).filter(StudentClass.class_id == class_id).all()
        student_ids = [s[0] for s in student_ids]  # Chuyển đổi kết quả thành danh sách ID

        if not student_ids:
            return 0  # Nếu không có học sinh trong lớp

        # Tính điểm trung bình cho từng học sinh
        average_scores = calculate_average_scores(
            student_ids=student_ids,
            semester_id=semester_id,
            subject_id=subject_id,
            year_id=year_id,
        )

        # Đếm số học sinh đạt điểm >= 5
        passed_count = sum(1 for score in average_scores.values() if score >= 5)

        logger.debug(f"Number of students passed: {passed_count}")
        return passed_count

    except Exception as e:
        logger.error(f"Error counting passed students: {str(e)}")
        return 0
