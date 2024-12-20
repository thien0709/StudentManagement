from manage_student import db
from manage_student.models import Student, Score, Subject, Semester, Class, Year, StudentClass, TeachingAssignment
from sqlalchemy.orm import aliased


from manage_student import db
from manage_student.models import Class

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

# Hàm lấy tên lớp học theo ID
def get_class_name(class_id):
    try:
        class_ = db.session.query(Class).get(class_id)
        return class_.name if class_ else None
    except Exception as e:
        print(f"Lỗi khi truy vấn tên lớp học: {str(e)}")
        return None
