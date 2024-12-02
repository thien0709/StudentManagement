import enum
import hashlib
from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Boolean, DateTime, Enum, Text, CheckConstraint
from sqlalchemy.orm import relationship

from manage_student import db, app


class UserRole(enum.Enum):
    STAFF = 1
    TEACHER = 2
    ADMIN = 3


class GRADE(enum.Enum):
    K10 = 10
    K11 = 11
    K12 = 12


class TypeExam(enum.Enum):
    EXAM_15P = 1
    EXAM_45P = 2
    EXAM_final = 3


class Profile(db.Model):
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(50))
    email = Column(String(50), unique=True)
    birthday = Column(DateTime)
    gender = Column(Boolean)
    address = Column(Text)
    phone = Column(String(10), unique=True)
    avatar = Column(String(200),
                    default='https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg')


class User(db.Model, UserMixin):
    id = Column(Integer, ForeignKey("profile.id"), primary_key=True, nullable=False, unique=True)
    username = Column(String(50), unique=True)
    password = Column(String(50))
    user_role = Column(Enum(UserRole))
    profile = relationship("Profile", backref="user", lazy=True)


class Staff(db.Model):
    id = Column(Integer, ForeignKey("user.id"), primary_key=True, unique=True, nullable=False)
    user = relationship("User", backref="staff", lazy=True)
    classes = relationship("Staff_Class", backref="staff", lazy=True)


class Admin(db.Model):
    id = Column(Integer, ForeignKey("user.id"), primary_key=True, unique=True, nullable=False)
    user = relationship("User", backref="admin", lazy=True)
    regulation = relationship("Regulation", backref="admin", lazy=True)


class Teacher(db.Model):
    id = Column(Integer, ForeignKey("user.id"), primary_key=True, unique=True, nullable=False)
    # class_teach = relationship("Class", backref="teacher", lazy=True)
    user = relationship("User", backref="teacher", lazy=True)
    subject = relationship("Teachers_Subject", backref="teacher", lazy=True)


class Subject(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    scores = relationship("Score", backref="subject", lazy=True)
    teacher = relationship("Teachers_Subject", backref="subject", lazy=True)


class Class(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    grade = Column(Enum(GRADE))
    # count = Column(Integer)
    amount = Column(Integer, default=0)
    year = Column(Integer, default=datetime.now().year)
    teacher_id = Column(Integer, ForeignKey("teacher.id"))
    students = relationship("Students_Classes", backref="class", lazy=True)
    staff = relationship("Staff_Class", backref="class", lazy=True)


class Student(db.Model):
    id = Column(Integer, ForeignKey("profile.id"), primary_key=True, unique=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    grade = Column(Enum(GRADE), default=GRADE.K10)
    classes = relationship("Students_Classes", backref="student", lazy=True)
    profile = relationship("Profile", backref="student", lazy=True)
    scores = relationship("Score", backref="student", lazy=True)


class Students_Classes(db.Model):
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    class_id = Column(Integer, ForeignKey("class.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("student.id"), nullable=False)


class Teachers_Subject(db.Model):
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey("teacher.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subject.id"), nullable=False)

    # teacher = relationship("Teacher", backref="teachers_subject", lazy=True)
    # subject = relationship("Subject", backref="subject_teacher", lazy=True)


class Staff_Class(db.Model):
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("class.id"), nullable=False)
    time = Column(DateTime, default=datetime.now())


class Semester(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    semester_name = Column(String(50))
    scores = relationship('Score', backref='semester', lazy=True)


class Year(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    scores = relationship('Score', backref='year', lazy=True)


# class Teaching_plan(db.Model):
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     score_deadline = Column(DateTime)
#     class_id = Column(Integer, ForeignKey(Class.id), nullable=False)
#     semester_id = Column(Integer, ForeignKey(Semester.id), nullable=False)
#     teacher_subject_id = Column(Integer, ForeignKey(Teachers_Subject.id), nullable=False)
#
#     teacher_subject = relationship("Teachers_Subject", backref="teaching_plan")
#     # subject_id = Column(Integer, ForeignKey(Subject.id), nullable=False)
#     # teacher_id = Column(Integer, ForeignKey(Teacher.id), nullable=False)
#
#     # teacher = relationship("Teacher", backref="teacher", lazy=True)
#     semester = relationship("Semester", backref="semester", lazy=True)
#     class_teach = relationship("Class", backref="teach", lazy=True)
#     # subject = relationship("Subject", backref="subject", lazy=True)

#
# class Exam(db.Model):
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     student_id = Column(Integer, ForeignKey(Student.id), nullable=False)
#     teach_plan_id = Column(Integer, ForeignKey(Teaching_plan.id), nullable=False)
#     scores = relationship("Score", backref="exam", lazy=True)
#
#     student = relationship("Student", backref="exam", lazy=True)
#     teach_plan = relationship("Teaching_plan", backref="exam", lazy=True)


class Score(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    score = Column(Float)
    type = Column(Enum(TypeExam))
    student_id = Column(Integer, ForeignKey("student.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subject.id"), nullable=False)
    semester_id = Column(Integer, ForeignKey("semester.id"), nullable=False)
    year_id = Column(Integer, ForeignKey("year.id"), nullable=False)

    __table_args__ = (
        CheckConstraint('score >= 0', name='check_age_min'),
        CheckConstraint('score <= 10', name='check_age_max'),
    )


class Regulation(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(50))
    regulation_name = Column(String(100))
    min = Column(Integer)
    max = Column(Integer)
    admin_id = Column(Integer, ForeignKey("admin.id"), nullable=False)


if __name__ == '__main__':
    with app.app_context():
        # pass
        db.create_all()

        # new_profile = Profile(
        # name="Jane Doe",
        # email="janedoe@example.com",
        # birthday="1995-05-15",
        # gender=False,
        # address="456 Elm Street",
        # phone="0987654321"
        # )
        #
        # new_user = User(
        # profile=new_profile,
        # username="janedoe",
        # password="anothersecurepassword",
        # user_role=UserRole.TEACHER
        # )
        #
        profiles = [
            Profile(name="John Doe", email="johndoe@example.com", birthday=datetime(2000, 5, 20), gender=True,
                    address="123 Main St", phone="0123456789"),
            Profile(name="Jane Smith", email="janesmith@example.com", birthday=datetime(2002, 7, 15), gender=False,
                    address="456 Elm St", phone="0987654321"),
            Profile(name="Alice Johnson", email="alicej@example.com", birthday=datetime(2001, 3, 10), gender=False,
                    address="789 Maple St", phone="0112233445"),
            Profile(name="Bob Brown", email="bobbrown@example.com", birthday=datetime(1999, 12, 25), gender=True,
                    address="321 Oak St", phone="0223344556")
        ]

        students = [
            Student(name="Student A", grade=GRADE.K10, profile=profiles[0]),
            Student(name="Student B", grade=GRADE.K11, profile=profiles[1]),
            Student(name="Student C", grade=GRADE.K12, profile=profiles[2]),
            Student(name="Student D", grade=GRADE.K10, profile=profiles[3])
        ]
        users = [
            User(username="thien", password=str(hashlib.md5("123".encode('utf-8')).hexdigest()), user_role=UserRole.STAFF, profile=profiles[0]),
            User(username="thien123", password=str(hashlib.md5("123".encode('utf-8')).hexdigest()), user_role=UserRole.TEACHER, profile=profiles[1]),
            User(username="thien000",password=str(hashlib.md5("123".encode('utf-8')).hexdigest()), user_role=UserRole.ADMIN, profile=profiles[2]),
            User(username="thien111",password=str(hashlib.md5("123".encode('utf-8')).hexdigest()), user_role=UserRole.STAFF, profile=profiles[3])
        ]
        # add_user("John Doe", "thien123", "123")
        # add_user("Jane Smith", "thien2004", "123")
        # add_user("Alice Johnson", "thien000", "123")
        subjects = [
            Subject(name="Mathematics"),
            Subject(name="Physics"),
            Subject(name="Chemistry"),
            Subject(name="Biology"),
            Subject(name="History")
        ]

        classes = [
            Class(grade=GRADE.K10, amount=25, year=2024),
            Class(grade=GRADE.K11, amount=30, year=2024),
            Class(grade=GRADE.K12, amount=20, year=2024)
        ]

        semesters = [
            Semester(semester_name="Semester 1"),
            Semester(semester_name="Semester 2")
        ]

        years = [
            Year(id=1, name="2024-2025"),
            Year(id=2, name="2025-2026")
        ]

        db.session.add_all(students + profiles + subjects + classes + semesters + years)
        db.session.commit()
        scores = [
            Score(score=8.5, type=TypeExam.EXAM_15P, student_id=1, subject_id=1, semester_id=1, year_id=1),
            Score(score=7.0, type=TypeExam.EXAM_45P, student_id=2, subject_id=2, semester_id=1, year_id=1),
            Score(score=9.0, type=TypeExam.EXAM_final, student_id=3, subject_id=3, semester_id=1,
                  year_id=1),
            Score(score=6.5, type=TypeExam.EXAM_15P, student_id=4, subject_id=4, semester_id=1, year_id=1),
        ]
        db.session.add_all(scores)
        db.session.commit()
