from manage_student import db
from manage_student.models import Score, ExamType
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_scores_by_filter(semester_id, subject_id, year_id):
    """Lấy điểm của học sinh dựa trên bộ lọc.

    Args:
      semester_id: ID của học kỳ.
      subject_id: ID của môn học.
      year_id: ID của năm học.

    Returns:
      Danh sách các object ExamScore chứa thông tin về điểm của học sinh.
    """
    scores = Score.query.filter_by(
        semester_id=semester_id,
        subject_id=subject_id,
        year_id=year_id
    ).all()
    return scores


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

        score_15_min = sum([score.score for score in scores if score.exam_type == ExamType.EXAM_15P])
        score_1_hour = sum([score.score for score in scores if score.exam_type == ExamType.EXAM_45P])
        final_exam = next((score.score for score in scores if score.exam_type == ExamType.EXAM_FINAL), 0)

        total_weight = len(scores) * 1 + len(scores) * 2 + 3  # Giả sử mỗi loại điểm có ít nhất 1 cột điểm
        average_score = (score_15_min + score_1_hour * 2 + final_exam * 3) / total_weight
        average_scores[student_id] = round(average_score, 2)

    return average_scores


def save_student_scores(student_id, score_15_min_list, score_1_hour_list, final_exam, subject_id, semester_id,
                        year_id):
    try:
        score_15_min_list = [float(score) for score in score_15_min_list if score is not None]
        score_1_hour_list = [float(score) for score in score_1_hour_list if score is not None]
        final_exam = float(final_exam) if final_exam else 0.0

        logger.debug(
            f"Saving scores for student {student_id}: 15min={score_15_min_list}, 1 hour={score_1_hour_list}, final_exam={final_exam}")

        # Xóa tất cả điểm cũ của học sinh
        Score.query.filter_by(
            student_id=student_id,
            subject_id=subject_id,
            semester_id=semester_id,
            year_id=year_id
        ).delete()

        # Lưu điểm 15 phút -> ExamScore
        for score in score_15_min_list:
            new_score = Score(
                student_id=student_id,
                score=score,
                exam_type=ExamType.EXAM_15P,
                subject_id=subject_id,
                semester_id=semester_id,
                year_id=year_id
            )
            db.session.add(new_score)

        # Lưu điểm 1 tiết -> ExamScore
        for score in score_1_hour_list:
            new_score = Score(
                student_id=student_id,
                score=score,
                exam_type=ExamType.EXAM_45P,
                subject_id=subject_id,
                semester_id=semester_id,
                year_id=year_id
            )
            db.session.add(new_score)

        # Lưu điểm cuối kỳ -> ExamScore
        new_score = Score(
            student_id=student_id,
            score=final_exam,
            exam_type=ExamType.EXAM_FINAL,
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