from manage_student import db
from manage_student.models import Student, Score, Subject, Semester, Class, Year, StudentClass
from manage_student.dao.class_dao import get_classes, get_subjects, get_semesters, get_years, get_students_by_filter
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

