from manage_student import db
from manage_student.models import Regulation

def get_max_students_in_class():
    regulation = db.session.query(Regulation).filter(Regulation.name == "Sĩ số lớp").first()
    return regulation.max_value if regulation else 30


