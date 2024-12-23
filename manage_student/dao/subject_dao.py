# Hàm lấy tất cả các môn học
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
