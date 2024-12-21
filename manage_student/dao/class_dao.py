from manage_student import db
from manage_student.models import Class, Grade


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


def get_grades():
    return [grade.name for grade in Grade]


def get_classes_by_grade(grade):
    # Ví dụ sử dụng SQLAlchemy để lấy danh sách lớp theo khối
    return Class.query.filter_by(grade=grade).all()
