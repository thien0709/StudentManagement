# Hàm lấy tất cả các năm học
from manage_student import db
from manage_student.models import Year


def get_years():
    try:
        return db.session.query(Year).all()
    except Exception as e:
        print(f"Lỗi khi truy vấn năm học: {str(e)}")
        return []