# Hàm lấy tất cả các năm học
from flask import jsonify

from manage_student import db
from manage_student.models import Year


def get_years():
    try:
        return db.session.query(Year).all()
    except Exception as e:
        print(f"Lỗi khi truy vấn năm học: {str(e)}")
        return []

def api_get_years():
    try:
        # Lấy tất cả các năm từ cơ sở dữ liệu
        years = Year.query.all()
        # Chuyển đổi thành danh sách JSON
        year_list = [{'id': y.id, 'name': y.name} for y in years]
        # Trả về dữ liệu dưới dạng JSON
        return jsonify({'years': year_list})
    except Exception as e:
        # Nếu có lỗi, trả về thông báo lỗi
        return jsonify({'error': str(e)}), 500
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
