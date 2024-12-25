from datetime import datetime
from enum import Enum as PyEnum

from flask_login import UserMixin
from sqlalchemy import (
    Column, String, Float, Integer, ForeignKey, Boolean, DateTime, Enum, Text, CheckConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime
from manage_student import db, app


class UserRole(PyEnum):
    STAFF = 1
    TEACHER = 2
    ADMIN = 3


class Grade(PyEnum):
    K10 = 10
    K11 = 11
    K12 = 12


class ExamType(PyEnum):
    EXAM_15P = 1
    EXAM_45P = 2
    EXAM_FINAL = 3


class Profile(db.Model):
    __tablename__ = "profile"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    birthday = Column(DateTime)
    gender = Column(Boolean)
    address = Column(Text)
    phone = Column(String(10), unique=True)

    def strftime(self, format):
        return self.birthday.strftime(format)


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = Column(Integer, ForeignKey("profile.id"), primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)
    role = Column(Enum(UserRole, name="user_role_enum"), nullable=False)
    avatar = Column(
        String(200),
        default="https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg",
    )
    # 1-1, User-Profile
    profile = relationship("Profile", backref="user", lazy=True, uselist=False)

    def get_id(self):
        return self.id

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def get_username(self):
        return self.username
    def get_password(self):
        return self.password
    def get_role(self):
        return self.role


class Staff(User):
    __tablename__ = "staff"
    id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    # 1-n: Staff-StaffClass
    classes = relationship("StaffClass", backref="staff", lazy=True)
    # 1-1, User-Staff
    user = relationship("User", backref="staff", lazy=True, uselist=False)


class Admin(User):
    __tablename__ = "admin"
    id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    # 1-n: Admin-Regulation
    regulations = relationship("Regulation", backref="admin", lazy=True)
    # 1-1, User-Admin
    user = relationship("User", backref="admin", lazy=True, uselist=False)


class Teacher(User):
    __tablename__ = "teacher"
    id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    # 1-n Một Teacher có nhiều TeachingAssignment
    assignment = relationship("TeachingAssignment", backref="teacher", lazy=True)
    # 1-1, User-Teacher
    user = relationship("User", backref="teacher", lazy=True, uselist=False)

    def name(self):
        # Lấy tên của giáo viên thông qua mối quan hệ với Profile
        return self.user.profile.name


class Subject(db.Model):
    __tablename__ = "subject"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    score_pass = Column(Float, default=5.0)
    # 1-n Một Subject có nhiều điểm
    scores = relationship("Score", backref="subject", lazy=True)
    # 1-n Một Subject có nhiều TeachingAssignment
    assignment = relationship("TeachingAssignment", backref="subject", lazy=True)


class Class(db.Model):
    __tablename__ = "class"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    amount = Column(Integer, default=0)
    grade = Column(Enum(Grade), default=Grade.K10)
    # year_id = Column(Integer, ForeignKey("year.id"), nullable=False)
    # teacher_id = Column(Integer, ForeignKey("teacher.id"))
    # n-n Một Class có nhiều Student
    students = relationship("StudentClass", backref="class", lazy=True)
    # n-n Một Class có nhiều Staff
    staff = relationship("StaffClass", backref="class", lazy=True)
    # 1-n Một Class có nhiều TeachingAssignment
    assignment = relationship("TeachingAssignment", backref="class", lazy=True)


class Student(db.Model):
    __tablename__ = "student"
    id = Column(Integer, ForeignKey("profile.id"), primary_key=True)  # 1-1: Mỗi Student có một Profile
    grade = Column(Enum(Grade), default=Grade.K10)
    # 1-1, Student-Profile
    profile = relationship("Profile", backref="student", uselist=False, lazy=True)

    # n-n Một Student có nhiều Class
    classes = relationship("StudentClass", backref="student", lazy=True)
    # 1-n Một Student có nhiều điểm
    scores = relationship("Score", backref="student", lazy=True)

    def name(self):
        return self.profile.name


class StudentClass(db.Model):
    __tablename__ = "student_class"
    id = Column(Integer, primary_key=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey("class.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("student.id"), nullable=False)


class TeachingAssignment(db.Model):
    __tablename__ = "teaching_assignment"
    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey("teacher.id"), nullable=False)
    subjects_id = Column(Integer, ForeignKey("subject.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("class.id"), nullable=False)
    semester_id = Column(Integer, ForeignKey("semester.id"), nullable=False)
    years_id = Column(Integer, ForeignKey("year.id"), nullable=False)


class StaffClass(db.Model):
    __tablename__ = "staff_class"
    id = Column(Integer, primary_key=True, autoincrement=True)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("class.id"), nullable=False)
    time = Column(DateTime, default=datetime.now)


class Semester(db.Model):
    __tablename__ = "semester"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    # 1-n Một Semester có nhiều điểm
    scores = relationship("Score", backref="semester", lazy=True)
    # 1-n Một Semester có nhiều TeachingAssignment
    assigment = relationship("TeachingAssignment", backref="semester", lazy=True)


class Year(db.Model):
    __tablename__ = "year"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    # Quan hệ 1-n với bảng Score (Mỗi Year có nhiều điểm)
    scores = relationship("Score", backref="year", lazy=True)
    # 1-n Một Year có nhiều TeachingAssignment
    assigment = relationship("TeachingAssignment", backref="year", lazy=True)


class Score(db.Model):
    __tablename__ = "score"
    id = Column(Integer, primary_key=True, autoincrement=True)
    score = Column(Float, nullable=False)
    exam_type = Column(Enum(ExamType), nullable=False)

    # 1-n Một Score thuộc về một Student
    student_id = Column(Integer, ForeignKey("student.id"), nullable=False)
    # 1-n Một Score thuộc về một Subject
    subject_id = Column(Integer, ForeignKey("subject.id"), nullable=False)
    # 1-n Một Score thuộc về một Semester
    semester_id = Column(Integer, ForeignKey("semester.id"), nullable=False)
    # 1-n Một Score thuộc về một Year
    year_id = Column(Integer, ForeignKey("year.id"), nullable=False)

    __table_args__ = (
        CheckConstraint("score >= 0", name="check_score_min"),
        CheckConstraint("score <= 10", name="check_score_max"),
    )


class Regulation(db.Model):
    __tablename__ = "regulation"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    min_value = Column(Integer)
    max_value = Column(Integer)
    # 1-n: Admin-Regulation
    admin_id = Column(Integer, ForeignKey("admin.id"), nullable=False)


if __name__ == "__main__":
    with app.app_context():
         db.create_all()
        # # Thêm Profiles
        # profiles = [
        #     Profile(name="Emily Davis", email="emily.davis@example.com", birthday=datetime(1992, 4, 15),
        #             gender=False, address="101 Willow St", phone="5551237890"),
        #     Profile(name="Frank Wilson", email="frank.wilson@example.com", birthday=datetime(1980, 12, 25),
        #             gender=True, address="202 Birch Ave", phone="5559876543"),
        #     Profile(name="Grace Miller", email="grace.miller@example.com", birthday=datetime(1987, 7, 10),
        #             gender=False, address="303 Pine Lane", phone="5556781234"),
        #     Profile(name="Harry Potter", email="harry.potter@example.com", birthday=datetime(1991, 6, 30),
        #             gender=True, address="404 Elm Dr", phone="5554321987"),
        #     Profile(name="Ivy Thompson", email="ivy.thompson@example.com", birthday=datetime(1990, 2, 20),
        #             gender=False, address="505 Maple Blvd", phone="5557654321"),
        #     Profile(name="Jack Moore", email="jack.moore@example.com", birthday=datetime(1995, 11, 11),
        #             gender=True, address="606 Cedar Rd", phone="5553219876"),
        #     Profile(name="Karen White", email="karen.white@example.com", birthday=datetime(1982, 9, 19),
        #             gender=False, address="707 Cherry Way", phone="5551234567"),
        #     Profile(name="Liam Scott", email="liam.scott@example.com", birthday=datetime(1989, 3, 5),
        #             gender=True, address="808 Ash Ct", phone="5556543210"),
        #     Profile(name="Mia Clark", email="mia.clark@example.com", birthday=datetime(1994, 8, 22),
        #             gender=False, address="909 Oak Pl", phone="5557890123"),
        #     Profile(name="Nathan Adams", email="nathan.adams@example.com", birthday=datetime(1985, 5, 18),
        #             gender=True, address="1010 Walnut St", phone="5558901234"),
        # ]
        # db.session.add_all(profiles)
        # db.session.commit()
        #
        # # Thêm Users
        # users = [
        #     User(id=1, username="emily", password="password1", role=UserRole.STAFF, profile=profiles[0]),
        #     User(id=2, username="frank", password="password2", role=UserRole.TEACHER, profile=profiles[1]),
        #     User(id=3, username="Grace", password="password3", role=UserRole.ADMIN, profile=profiles[2]),
        # ]
        # db.session.add_all(users)
        # db.session.commit()
        #
        # # Thêm Staff, Teacher, Admin
        # staff = Staff(id=users[0].id, user=users[0])
        # teacher = Teacher(id=users[1].id, user=users[1])
        # admin = Admin(id=users[2].id, user=users[2])
        # db.session.add_all([staff, teacher, admin])
        # db.session.commit()

        # Thêm Subjects
        # subjects = [
        #     Subject(name="Mathematics"),
        #     Subject(name="Science"),
        #     Subject(name="History"),
        # ]
        # db.session.add_all(subjects)
        # db.session.commit()
        #
        # # Thêm Classes
        # classes = [
        #     Class(name="10a3", amount=25),
        #     Class(name="10a4", amount=38),
        #     Class(name="10a5", amount=29),
        #     Class(name="10a6", amount=40),
        #     Class(name="10a7", amount=45),
        # ]
        # db.session.add_all(classes)
        # db.session.commit()
        #
        # # Thêm Students
        # students = [
        #     Student(id=1, grade=Grade.K10),  # Profile ID 4
        #     Student(id=2, grade=Grade.K11),  # Profile ID 5
        #     Student(id=3, grade=Grade.K12),  # Profile ID 6
        # ]
        # db.session.add_all(students)
        # db.session.commit()
        #
        # # Thêm Semesters và Years
        # semesters = [
        #     Semester(name="First Semester"),
        #     Semester(name="Second Semester"),
        # ]
        # year = Year(name="2024-2025")
        # db.session.add_all(semesters + [year])
        # db.session.commit()
        #
        # # Thêm Scores
        # scores = [
        #     Score(score=8.5, exam_type=ExamType.EXAM_FINAL, student_id=students[0].id, subject_id=subjects[0].id,
        #           semester_id=semesters[0].id, year_id=year.id),
        #     Score(score=7.0, exam_type=ExamType.EXAM_45P, student_id=students[1].id, subject_id=subjects[0].id,
        #           semester_id=semesters[0].id, year_id=year.id),
        # ]
        # db.session.add_all(scores)
        # db.session.commit()
        #
        # # Thêm Regulations
        # regulation = Regulation(name="Attendance Policy", min_value=75, max_value=100, admin_id=1)
        # db.session.add(regulation)
        # db.session.commit()
        # print("Dữ liệu mẫu đã được thêm thành công vào cơ sở dữ liệu!")
