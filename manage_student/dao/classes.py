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

def get_students_by_class(class_id=None, semester_id=None, year_id=None):
    query = db.session.query(Student).join(Students_Classes).join(Class).join(Year).join(Semester)
    if class_id:
        query = query.filter(Class.id == class_id)
    if semester_id:
        query = query.filter(Semester.id == semester_id)
    if year_id:
        query = query.filter(Year.id == year_id)
    return query.all()

def count_students_by_class(class_id=None):
    query = db.session.query(Student)
    if class_id:
        query = query.join(Students_Classes).join(Class).filter(Class.id == class_id)
    return query.count()