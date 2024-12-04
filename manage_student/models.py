import enum
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import (
    Column, String, Float, Integer, ForeignKey, Boolean, DateTime, Enum, Text, CheckConstraint
)
from sqlalchemy.orm import relationship
from manage_student import db, app


class UserRole(enum.Enum):
    STAFF = 1
    TEACHER = 2
    ADMIN = 3


class Grade(enum.Enum):
    K10 = 10
    K11 = 11
    K12 = 12


class ExamType(enum.Enum):
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


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = Column(Integer, ForeignKey("profile.id"), primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)
    avatar = Column(
        String(200),
        default="https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg",
    )
    user_role = Column(Enum(UserRole), nullable=False)
    # 1-1, User-Profile
    profile = relationship("Profile", backref="user", lazy=True, uselist=False)

class Staff(db.Model):
    __tablename__ = "staff"
    id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    # 1-n: Staff-StaffClass
    classes = relationship("StaffClass", backref="staff", lazy=True)
    # 1-1, User-Staff
    user = relationship("User", backref="staff", lazy=True, uselist=False)

class Admin(db.Model):
    __tablename__ = "admin"
    id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    # 1-n: Admin-Regulation
    regulations = relationship("Regulation", backref="admin", lazy=True)
    # 1-1, User-Admin
    user = relationship("User", backref="admin", lazy=True,uselist=False)

class Teacher(db.Model):
    __tablename__ = "teacher"
    id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    # 1-n Một Teacher có nhiều TeachingAssignment
    assignment = relationship("TeachingAssignment", backref="teacher", lazy=True)
    # 1-1, User-Teacher
    user = relationship("User", backref="teacher", lazy=True, uselist=False)
class Subject(db.Model):
    __tablename__ = "subject"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    # 1-n Một Subject có nhiều điểm
    scores = relationship("Score", backref="subject", lazy=True)
    # 1-n Một Subject có nhiều TeachingAssignment
    assignment = relationship("TeachingAssignment", backref="subject", lazy=True)
class Class(db.Model):
    __tablename__ = "class"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    amount = Column(Integer, default=0)
    year_id = Column(Integer, ForeignKey("year.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teacher.id"))

    # n-n Một Class có nhiều Student
    students = relationship("StudentClass", backref="class", lazy=True)
    # n-n Một Class có nhiều Staff
    staff = relationship("StaffClass", backref="class", lazy=True)
    #1-n Một Class thuộc về một Year
    year = relationship("Year", backref="classes", lazy=True)
    #1-n Một Class có nhiều TeachingAssignment
    assignment = relationship("TeachingAssignment", backref="class", lazy=True)


class Student(db.Model):
    __tablename__ = "student"
    id = Column(Integer, ForeignKey("profile.id"), primary_key=True)  # 1-1: Mỗi Student có một Profile
    name = Column(String(50), nullable=False, unique=True)
    grade = Column(Enum(Grade), default=Grade.K10)
    #1-1, Student-Profile
    profile = relationship("Profile", backref="student", uselist=False, lazy=True)

    #n-n Một Student có nhiều Class
    classes = relationship("StudentClass", backref="student", lazy=True)
    #1-n Một Student có nhiều điểm
    scores = relationship("Score", backref="student", lazy=True)


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
    type = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    min_value = Column(Integer)
    max_value = Column(Integer)
    # 1-n: Admin-Regulation
    admin_id = Column(Integer, ForeignKey("admin.id"), nullable=False)


if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()

        profiles = [
            Profile(name="John Doe", email="johndoe@example.com", birthday=datetime(2000, 5, 20), gender=True,
                    address="123 Main St", phone="0123456789"),
            Profile(name="Jane Smith", email="janesmith@example.com", birthday=datetime(2002, 7, 15),
                    gender=False,
                    address="456 Elm St", phone="0987654321"),
            Profile(name="Alice Johnson", email="alicej@example.com", birthday=datetime(2001, 3, 10),
                    gender=False,
                    address="789 Maple St", phone="0112233445"),
            Profile(name="Bob Brown", email="bobbrown@example.com", birthday=datetime(1999, 12, 25),
                    gender=True,        address="321 Oak St", phone="0223344556")
                    ]
        users = [
            User(username="johndoe", password="hashedpassword1", user_role=UserRole.STAFF, profile=profiles[0]),
            User(username="janesmith", password="hashedpassword2", user_role=UserRole.TEACHER, profile=profiles[1]),
            User(username="alicej", password="hashedpassword3", user_role=UserRole.ADMIN, profile=profiles[2]),
            # User(username="bobbrown", password="hashedpassword4", user_role=UserRole.STAFF, profile=profiles[3])
        ]
        students = [
            Student(name="Student A", grade=Grade.K10, profile=profiles[0]),
            Student(name="Student B", grade=Grade.K11, profile=profiles[1]),
            Student(name="Student C", grade=Grade.K12, profile=profiles[2])
        ]

        subjects = [
            Subject(name="Mathematics"),
            Subject(name="Physics"),
            Subject(name="Chemistry"),
            Subject(name="Biology"),
            Subject(name="History")
        ]

        years = [
            Year(name="2024-2025"),
            Year(name="2025-2026")
        ]

        classes = [
            Class(name="10A1", amount=25, year=years[0]),
            Class(name="10A2", amount=30, year=years[1]),
            Class(name="10A3", amount=20, year=years[0]),
        ]

        semesters = [
            Semester(name="Semester 1"),
            Semester(name="Semester 2")
        ]

        students_classes = [
            StudentClass(class_id=1, student_id=1),  # Student A thuộc lớp 10A1
            StudentClass(class_id=1, student_id=2),  # Student B thuộc lớp 10A1
            StudentClass(class_id=2, student_id=3),  # Student C thuộc lớp 10A2
        ]

        scores = [
            Score(score=9.0, exam_type="EXAM_FINAL", student_id=1, subject_id=3, semester_id=1, year_id=1),
            Score(score=8.5, exam_type="EXAM_FINAL", student_id=2, subject_id=2, semester_id=1, year_id=1),
            Score(score=7.5, exam_type="EXAM_FINAL", student_id=3, subject_id=1, semester_id=1, year_id=1)
            # Thêm đúng student_id
        ]


        with app.app_context():
            db.create_all()

            db.session.add_all(profiles + users + students + subjects + classes + semesters + years)
            db.session.commit()
            db.session.add_all(students_classes + scores)
            db.session.commit()

            print("Dữ liệu mẫu đã được thêm thành công!")