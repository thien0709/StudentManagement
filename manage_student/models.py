from enum import Enum as PyEnum
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import (
    Column, String, Float, Integer, ForeignKey, Boolean, DateTime, Enum, Text, CheckConstraint
)
from sqlalchemy.orm import relationship
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
    name = Column(String(50), nullable=False, unique=True)
    grade = Column(Enum(Grade), default=Grade.K10)
    # 1-1, Student-Profile
    profile = relationship("Profile", backref="student", uselist=False, lazy=True)

    # n-n Một Student có nhiều Class
    classes = relationship("StudentClass", backref="student", lazy=True)
    # 1-n Một Student có nhiều điểm
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

class ExamScore(db.Model):
    __tablename__ = "exam_score"
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subject.id"), nullable=False)
    semester_id = Column(Integer, ForeignKey("semester.id"), nullable=False)
    year_id = Column(Integer, ForeignKey("year.id"), nullable=False)
    exam_type = Column(Enum(ExamType), nullable=False)
    score = Column(Float, nullable=False)

    __table_args__ = (
        CheckConstraint("score >= 0", name="check_exam_score_min"),
        CheckConstraint("score <= 10", name="check_exam_score_max"),
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
        pass
        # db.drop_all()
        # db.create_all()
        # # Profile
        # profile1 = Profile(name="Alice Smith", email="alice@example.com", birthday=datetime(1990, 1, 1),
        #                    gender=True, address="123 Main St", phone="1234567890")
        # profile2 = Profile(name="Bob Johnson", email="bob@example.com", birthday=datetime(1985, 5, 5), gender=False,
        #                    address="456 Elm St", phone="0987654321")
        # profile3 = Profile(name="Charlie Brown", email="charlie@example.com", birthday=datetime(1995, 7, 7),
        #                    gender=True, address="789 Oak St", phone="5678901234")
        #
        # db.session.add_all([profile1, profile2, profile3])
        # db.session.commit()
        #
        # # Users
        # user1 = User(username="alice", password="password", role=UserRole.STAFF, profile=profile1)
        # user2 = User(username="bob", password="password", role=UserRole.TEACHER, profile=profile2)
        # user3 = User(username="charlie", password="password", role=UserRole.ADMIN, profile=profile3)
        #
        # db.session.add_all([user1, user2, user3])
        # db.session.commit()
        #
        # # Staff, Admin, Teacher
        # staff1 = Staff(id=user1.id, user=user1)
        # admin1 = Admin(id=user3.id, user=user3)
        # teacher1 = Teacher(id=user2.id, user=user2)
        #
        # db.session.add_all([staff1, admin1, teacher1])
        # db.session.commit()
        #
        # Subjects
        # subject1 = Subject(name="Mathematics")
        # subject2 = Subject(name="Science")
        # subject3 = Subject(name="History")
        #
        # db.session.add_all([subject1, subject2, subject3])
        # db.session.commit()

        # # Classes
        # class1 = Class(name="Class A", amount=25)
        # class2 = Class(name="Class B", amount=30)
        #
        # db.session.add_all([class1, class2])
        # db.session.commit()

        # # Students
        # student1 = Student(id=1, name="Alice Smith", grade=Grade.K10)
        # student2 = Student(id=2, name="Bob Johnson", grade=Grade.K11)
        # student3 = Student(id=3, name="Charlie Brown", grade=Grade.K12)
        #
        # db.session.add_all([student1, student2, student3])
        # db.session.commit()

        # # StudentClass
        # student_class1 = StudentClass(class_id=class1.id, student_id=student1.id)
        # student_class2 = StudentClass(class_id=class2.id, student_id=student2.id)
        # student_class3 = StudentClass(class_id=class1.id, student_id=student3.id)
        #
        # db.session.add_all([student_class1, student_class2, student_class3])
        # db.session.commit()
        #
        # # Semesters and Years
        # semester1 = Semester(name="First Semester")
        # semester2 = Semester(name="Second Semester")
        #
        # year1 = Year(name="2024-2025")
        #
        # db.session.add_all([semester1, semester2, year1])
        # db.session.commit()

        # # TeachingAssignments
        # teaching_assignment1 = TeachingAssignment(teacher_id=3, subjects_id=1,
        #                                           class_id=1, semester_id=1, years_id=1)
        # teaching_assignment2 = TeachingAssignment(teacher_id=3, subjects_id=1,
        #                                           class_id=1, semester_id=2, years_id=1)
        #
        # db.session.add_all([teaching_assignment1, teaching_assignment2])
        # db.session.commit()
        #
        # # StaffClasses
        # staff_class1 = StaffClass(staff_id=2, class_id=1, time=datetime.now())
        # staff_class2 = StaffClass(staff_id=2, class_id=1, time=datetime.now())
        #
        # db.session.add_all([staff_class1, staff_class2])
        # db.session.commit()


        #
        # Scores
        # score1 = Score(score=8.5, exam_type=ExamType.EXAM_FINAL, student_id=1, subject_id=1,
        #                semester_id=1, year_id=1)
        # score2 = Score(score=7.0, exam_type=ExamType.EXAM_45P, student_id=2, subject_id=1,
        #                semester_id=1, year_id=1)
        #
        # db.session.add_all([score1, score2])
        # db.session.commit()
        #
        # # Regulations
        # regulation1 = Regulation(type="General", name="Attendance Policy", min_value=75, max_value=100,
        #                          admin_id=1)
        #
        # db.session.add(regulation1)
        # db.session.commit()


