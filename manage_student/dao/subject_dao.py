# Hàm lấy tất cả các môn học
from manage_student import db
from manage_student.models import Subject


def get_subjects():
    try:
        return db.session.query(Subject).all()
    except Exception as e:
        print(f"Lỗi khi truy vấn môn học: {str(e)}")
        return []

