# Hàm lấy tất cả các năm học
from manage_student import db
from manage_student.models import Year


def get_years():
    try:
        return db.session.query(Year).all()
    except Exception as e:
        print(f"Lỗi khi truy vấn năm học: {str(e)}")
        return []

def get_year_name(year_id):
    try:
        year = db.session.query(Year).filter_by(id=year_id).first()
        if year:
            return year.name
        else:
            print(f"Không tìm thấy năm học với ID: {year_id}")
            return None
    except Exception as e:
        print(f"Lỗi khi truy vấn tên năm học: {str(e)}")
        return None
