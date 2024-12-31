# Hàm lấy tất cả các môn học
from flask import jsonify

from manage_student import db
from manage_student.models import Subject


from manage_student import db
from manage_student.models import Subject

# Hàm lấy tất cả các môn học
def get_subjects():
    try:
        return db.session.query(Subject).all()
    except Exception as e:
        print(f"Lỗi khi truy vấn môn học: {str(e)}")
        return []

# Hàm lấy tên môn học theo ID
def get_subject_name(subject_id):
    try:
        subject = db.session.query(Subject).get(subject_id)
        return subject.name if subject else None
    except Exception as e:
        print(f"Lỗi khi truy vấn tên môn học: {str(e)}")
        return None


def api_get_subjects():
    try:
        # Lấy tất cả các môn học từ cơ sở dữ liệu
        subjects = Subject.query.all()

        # Kiểm tra xem danh sách môn học có rỗng không
        if not subjects:
            print("Danh sách môn học rỗng.")
        else:
            print(f"Truy vấn thành công: {subjects}")

        # Chuyển đổi thành danh sách JSON
        subject_list = [{'id': s.id, 'name': s.name} for s in subjects]
        # Trả về dữ liệu dưới dạng JSON
        return jsonify({'subjects': subject_list})
    except Exception as e:
        # Nếu có lỗi, in lỗi và trả về thông báo lỗi
        print(f"Lỗi API: {str(e)}")
        return jsonify({'error': str(e)}), 500