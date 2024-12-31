# Hàm lấy tất cả các học kỳ
from flask import jsonify

from manage_student import db
from manage_student.models import Semester


from manage_student import db
from manage_student.models import Semester

# Hàm lấy tất cả các học kỳ
def get_semesters():
    try:
        semesters = db.session.query(Semester).all()
        if not semesters:
            print("Không có học kỳ trong cơ sở dữ liệu.")
        return semesters
    except Exception as e:
        print(f"Lỗi khi truy vấn học kỳ: {str(e)}")
        return []

# Hàm lấy tên học kỳ theo ID
def get_semester_name(semester_id):
    try:
        semester = db.session.query(Semester).get(semester_id)
        return semester.name if semester else None
    except Exception as e:
        print(f"Lỗi khi truy vấn tên học kỳ: {str(e)}")
        return None

def api_get_semesters():
    try:
        # Lấy danh sách học kỳ từ cơ sở dữ liệu
        semesters = Semester.query.all()
        # Chuyển đổi thành danh sách JSON
        semester_list = [{'id': s.id, 'name': s.name} for s in semesters]
        # Trả về dữ liệu dưới dạng JSON
        return jsonify({'semesters': semester_list})
    except Exception as e:
        # Nếu có lỗi, trả về thông báo lỗi
        return jsonify({'error': str(e)}), 500