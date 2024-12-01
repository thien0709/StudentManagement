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


class User(db.Model, UserMixin):
    id = Column(Integer, ForeignKey("profile.id"), primary_key=True, nullable=False, unique=True)
    username = Column(String(50), unique=True)
    password = Column(String(50))
    avatar = Column(String(200),
                    default='https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg')
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
        # Tạo các profile
        # Tạo đối tượng Profile
        new_profile = Profile(
            name="Jane Doe",
            email="janedoe@example.com",
            birthday="1995-05-15",
            gender=False,
            address="456 Elm Street",
            phone="0987654321"
        )

        # Tạo đối tượng User liên kết với Profile
        new_user = User(
            profile=new_profile,
            username="janedoe",
            password="anothersecurepassword",
            user_role=UserRole.TEACHER
        )

        # Thêm cả hai vào session và commit
        db.session.add(new_user)
        db.session.commit()

        print(f"Profile and User added with Profile ID: {new_profile.id}, User ID: {new_user.id}")

        # # Thêm nhiều Subject
        # subjects = [
        #     Subject(name="Mathematics"),
        #     Subject(name="Physics"),
        #     Subject(name="Chemistry"),
        #     Subject(name="Biology"),
        #     Subject(name="History")
        # ]
        #
        # # Thêm nhiều Class
        # classes = [
        #     Class(grade=GRADE.K10, amount=25, year=2024),
        #     Class(grade=GRADE.K11, amount=30, year=2024),
        #     Class(grade=GRADE.K12, amount=20, year=2024)
        # ]
        #
        # # Thêm nhiều Student
        # students = [
        #     Student(name="Student A", grade=GRADE.K10, profile=profiles[0]),
        #     Student(name="Student B", grade=GRADE.K11, profile=profiles[1]),
        #     Student(name="Student C", grade=GRADE.K12, profile=profiles[2]),
        #     Student(name="Student D", grade=GRADE.K10, profile=profiles[3])
        # ]
        #
        # # Thêm nhiều Score
        # scores = [
        #     Score(score=8.5, type=TypeExam.EXAM_15P, student_id=1, subject_id=1, semester_id=1, year_id=1),
        #     Score(score=7.0, type=TypeExam.EXAM_45P, student_id=2, subject_id=2, semester_id=1, year_id=1),
        #     Score(score=9.0, type=TypeExam.EXAM_final, student_id=3, subject_id=3, semester_id=1, year_id=1),
        #     Score(score=6.5, type=TypeExam.EXAM_15P, student_id=4, subject_id=4, semester_id=1, year_id=1)
        # ]
        #
