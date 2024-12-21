from manage_student import db
from manage_student.models import Score, Student, Profile, Subject, StudentClass, Class, TeachingAssignment

def get_students_by_filter(class_id=None, semester_id=None, subject_id=None, year_id=None):
    query = db.session.query(Student)

    if class_id:
        query = query.join(StudentClass, Student.id == StudentClass.student_id) \
            .join(Class, Class.id == StudentClass.class_id) \
            .filter(Class.id == class_id)

    if semester_id or year_id or subject_id:
        student_class_alias = db.aliased(StudentClass)
        query = query.join(student_class_alias, Student.id == student_class_alias.student_id) \
            .join(TeachingAssignment, student_class_alias.class_id == TeachingAssignment.class_id)
        if semester_id:
            query = query.filter(TeachingAssignment.semester_id == semester_id)
        if year_id:
            query = query.filter(TeachingAssignment.years_id == year_id)
        if subject_id:
            query = query.filter(TeachingAssignment.subjects_id == subject_id)

    # Join với Profile để lấy tên từ bảng Profile
    query = query.join(Profile, Student.id == Profile.id)

    # debug
    print(query.statement.compile(dialect=db.engine.dialect))

    try:
        students = query.all()
        if not students:
            print("Không có học sinh nào thỏa mãn điều kiện.")
        return students  # Trả về danh sách đối tượng Student

    except Exception as e:
        print(f"Lỗi khi truy vấn học sinh: {str(e)}")
        return []