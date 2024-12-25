from manage_student import db
from manage_student.models import Regulation


class RegulationDAO:
    def get_max_students_in_class(class_id):
        regulation = db.session.query(Regulation).filter(Regulation.class_id == class_id).first()

        if regulation:
            return regulation.max_value
        return None
