# Hàm lấy tất cả các học kỳ
from manage_student import db
from manage_student.models import Semester


def get_semesters():
    try:
        semesters = db.session.query(Semester).all()
        if not semesters:
            print("Không có học kỳ trong cơ sở dữ liệu.")
        return semesters
    except Exception as e:
        print(f"Lỗi khi truy vấn học kỳ: {str(e)}")
        return []
