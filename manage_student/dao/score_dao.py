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
    """
    Tính toán điểm trung bình cho mỗi học sinh.

    Args:
      student_ids: Danh sách ID của học sinh.
      semester_id: ID của học kỳ (optional).
      subject_id: ID của môn học (optional).
      year_id: ID của năm học (optional).

    Returns:
      Một dictionary với key là student_id và value là điểm trung bình tương ứng.
    """
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

        total_weight = 0
        weighted_sum = 0
        for score in scores:
            if score.exam_type == ExamType.EXAM_15P:
                weight = 1
            elif score.exam_type == ExamType.EXAM_45P:
                weight = 2
            elif score.exam_type == ExamType.EXAM_FINAL:
                weight = 3
            else:
                weight = 0  # Hoặc xử lý các loại bài kiểm tra khác

            weighted_sum += score.score * weight
            total_weight += weight

        if total_weight > 0:
            average_scores[student_id] = round(weighted_sum / total_weight, 2)
        else:
            average_scores[student_id] = 0

    return average_scores


def save_student_scores(student_id, score_15_min_list, score_1_hour_list, final_exam, subject_id, semester_id, year_id):
    try:
        score_15_min_list = [float(score) for score in score_15_min_list if score is not None]
        score_1_hour_list = [float(score) for score in score_1_hour_list if score is not None]
        final_exam = float(final_exam) if final_exam else 0.0

        logger.debug(f"Saving scores for student {student_id}: 15min={score_15_min_list}, 1 hour={score_1_hour_list}, final_exam={final_exam}")

        # Xóa điểm cũ
        delete_count = Score.query.filter_by(student_id=student_id, subject_id=subject_id, semester_id=semester_id, year_id=year_id).delete()
        logger.debug(f"Deleted {delete_count} old scores for student {student_id}")

        # Lưu điểm 15 phút
        for score in score_15_min_list:
            new_score = Score(student_id=student_id, score=score, exam_type=ExamType.EXAM_15P, subject_id=subject_id, semester_id=semester_id, year_id=year_id)
            db.session.add(new_score)

        # Lưu điểm 1 tiết
        for score in score_1_hour_list:
            new_score = Score(student_id=student_id, score=score, exam_type=ExamType.EXAM_45P, subject_id=subject_id, semester_id=semester_id, year_id=year_id)
            db.session.add(new_score)

        # Lưu điểm cuối kỳ
        new_score = Score(student_id=student_id, score=final_exam, exam_type=ExamType.EXAM_FINAL, subject_id=subject_id, semester_id=semester_id, year_id=year_id)
        db.session.add(new_score)

        # Commit transaction
        db.session.commit()
        logger.debug("Scores saved successfully.")
        return "Lưu điểm thành công"

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving scores: {str(e)}")
        return f"Đã xảy ra lỗi: {str(e)}"
