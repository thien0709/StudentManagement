from manage_student import db
from manage_student.models import Regulation

def get_max_students_in_class():
    regulation = db.session.query(Regulation).filter(Regulation.name == "Sĩ số lớp").first()
    return regulation.max_value if regulation else 40

def get_min_class_in_grade():
    regulation = db.session.query(Regulation).filter(Regulation.name == "Số lớp tối thiểu").first()
    return regulation.min_value if regulation else 1

def get_min_age():
    # Lấy giá trị min_value đầu tiên từ bảng regulations (hoặc tìm theo tên quy định nếu cần)
    regulation = Regulation.query.filter_by(name="Độ tuổi").first()
    if regulation:
        return regulation.min_value
    return 15

def get_max_age():
    # Lấy giá trị max_value đầu tiên từ bảng regulations (hoặc tìm theo tên quy định nếu cần)
    regulation = Regulation.query.filter_by(name="Độ tuổi").first()
    if regulation:
        return regulation.max_value
    return 20
