
import logging
from manage_student import db
from manage_student.models import Score, ExamType, Student, StudentClass

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
        filters = {}
        if semester_id:
            filters['semester_id'] = semester_id
        if subject_id:
            filters['subject_id'] = subject_id
        if year_id:
            filters['year_id'] = year_id
        query = query.filter_by(**filters)

        scores = query.all()
        logger.debug(f"Student {student_id} scores: {scores}")

        total_weight = 0
        weighted_sum = 0
        for score in scores:
            weight = {
                ExamType.EXAM_15P: 1,
                ExamType.EXAM_45P: 2,
                ExamType.EXAM_FINAL: 3
            }.get(score.exam_type, 0)

            weighted_sum += score.score * weight
            total_weight += weight

        logger.debug(f"Total weight for student {student_id}: {total_weight}, Weighted sum: {weighted_sum}")

        if total_weight > 0:
            average_scores[student_id] = round(weighted_sum / total_weight, 2)
        else:
            average_scores[student_id] = 0

        logger.debug(f"Average score for student {student_id}: {average_scores[student_id]}")

    return average_scores



def save_student_scores(student_id, score_15_min_list, score_1_hour_list, final_exam, subject_id, semester_id, year_id):
    try:
        score_15_min_list = [float(score) for score in score_15_min_list if score is not None]
        score_1_hour_list = [float(score) for score in score_1_hour_list if score is not None]
        final_exam = float(final_exam) if final_exam else 0.0

        # Làm tròn điểm trước lưu
        score_15_min_list = [round(score, 2) for score in score_15_min_list]
        score_1_hour_list = [round(score, 2) for score in score_1_hour_list]
        final_exam = round(final_exam, 2)

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

