from manage_student import db
from manage_student.models import TeachingAssignment, Teacher, Subject, Class, Semester, Year


def add_teaching_assignment(teacher_id, subjects_id, class_id, semester_id, years_id):
    """
    Thêm một bài phân công giảng dạy mới vào cơ sở dữ liệu.

    Args:
        teacher_id (int): ID của giáo viên.
        subjects_id (int): ID của môn học.
        class_id (int): ID của lớp học.
        semester_id (int): ID của học kỳ.
        years_id (int): ID của năm học.

    Returns:
        TeachingAssignment: Đối tượng vừa được thêm vào.
    """
    try:
        # Tạo đối tượng mới
        new_assignment = TeachingAssignment(
            teacher_id=teacher_id,
            subjects_id=subjects_id,
            class_id=class_id,
            semester_id=semester_id,
            years_id=years_id
        )

        # Thêm vào cơ sở dữ liệu
        db.session.add(new_assignment)
        db.session.commit()

        return new_assignment
    except Exception as e:
        db.session.rollback()  # Rollback nếu có lỗi
        print(f"Error when adding teaching assignment: {e}")
        return None


def delete_teaching_assignment(assignment_id):
    try:
        assignment = TeachingAssignment.query.get(assignment_id)
        if assignment:
            db.session.delete(assignment)
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        print(f"Error when deleting teaching assignment: {e}")
        return False


def check_assignment(assignments, class_id, subject_id, semester_id, year_id):
    for assignment in assignments:
        if (assignment.class_id == class_id and
            assignment.subjects_id == subject_id and
            assignment.semester_id == semester_id and
            assignment.years_id == year_id):
            return True
    return False

def get_all_assignments():
    """
    Lấy danh sách tất cả các phân công với thông tin chi tiết.
    """
    assignments = (
        db.session.query(TeachingAssignment)
        .join(Teacher, TeachingAssignment.teacher_id == Teacher.id)
        .join(Class, TeachingAssignment.class_id == Class.id)
        .join(Subject, TeachingAssignment.subjects_id == Subject.id)
        .join(Semester, TeachingAssignment.semester_id == Semester.id)
        .join(Year, TeachingAssignment.years_id == Year.id)
        .all()
    )

    result = []
    for assignment in assignments:
        result.append({
            "assignment_id": assignment.id,
            "teacher_name": assignment.get_teacher(),
            "class_name": assignment.get_class(),
            "subject_name": assignment.get_subject(),
            "semester_name": assignment.get_semester(),
            "year_name": assignment.get_year(),
        })

    return result
