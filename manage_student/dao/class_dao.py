from manage_student import db
from manage_student.models import Student, Score, Subject, Semester, Class, Year, StudentClass, TeachingAssignment
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

