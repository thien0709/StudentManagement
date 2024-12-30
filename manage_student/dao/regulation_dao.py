from manage_student import db
from manage_student.models import Regulation

def get_max_students_in_class():
    regulation = db.session.query(Regulation).filter(Regulation.name == "Sĩ số lớp").first()
    return regulation.max_value if regulation else 40

def get_min_class_in_grade():
    regulation = db.session.query(Regulation).filter(Regulation.name == "Số lớp tối thiểu").first()
    return regulation.min_value if regulation else 1