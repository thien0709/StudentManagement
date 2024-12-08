from manage_student import db
from manage_student.models import Score, Student, Subject, StudentClass, Class, ExamScore


def get_students_by_filter(class_id=None, semester_id=None, subject_id=None, year_id=None):
    query = db.session.query(Student)

    if class_id:
        query = query.join(StudentClass, Student.id == StudentClass.student_id) \
            .join(Class, Class.id == StudentClass.class_id) \
            .filter(Class.id == class_id)

    if semester_id or year_id or subject_id:
        query = query.join(ExamScore, Student.id == ExamScore.student_id)
        if semester_id:
            query = query.filter(ExamScore.semester_id == semester_id)
        if year_id:
            query = query.filter(ExamScore.year_id == year_id)
        if subject_id:
            query = query.join(Subject, Subject.id == ExamScore.subject_id) \
                .filter(Subject.id == subject_id)

    try:
        students = query.all()
        if not students:
            print("Không có học sinh nào thỏa mãn điều kiện.")
        return students
    except Exception as e:
        print(f"Lỗi khi truy vấn học sinh: {str(e)}")
        return []


def count_students_by_class(class_id=None):
    query = db.session.query(Student)
    if class_id:
        query = query.join(StudentClass).join(Class).filter(Class.id == class_id)
    return query.count()