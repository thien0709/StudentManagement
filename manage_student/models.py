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
    # grade = Column(Enum(Grade), default=Grade.K10)
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
        # pass
        # db.drop_all()
        # db.create_all()
        # # Profile
        # Tạo các hồ sơ mẫu
        # profile1 = Profile(name="Emily Davis", email="emily.davis@example.com", birthday=datetime(1992, 4, 15),
        #                    gender=False, address="101 Willow St", phone="5551237890")
        # profile2 = Profile(name="Frank Wilson", email="frank.wilson@example.com", birthday=datetime(1980, 12, 25),
        #                    gender=True, address="202 Birch Ave", phone="5559876543")
        # profile3 = Profile(name="Grace Miller", email="grace.miller@example.com", birthday=datetime(1987, 7, 10),
        #                    gender=False, address="303 Pine Lane", phone="5556781234")
        # profile4 = Profile(name="Harry Potter", email="harry.potter@example.com", birthday=datetime(1991, 6, 30),
        #                    gender=True, address="404 Elm Dr", phone="5554321987")
        # profile5 = Profile(name="Ivy Thompson", email="ivy.thompson@example.com", birthday=datetime(1990, 2, 20),
        #                    gender=False, address="505 Maple Blvd", phone="5557654321")
        # profile6 = Profile(name="Jack Moore", email="jack.moore@example.com", birthday=datetime(1995, 11, 11),
        #                    gender=True, address="606 Cedar Rd", phone="5553219876")
        # profile7 = Profile(name="Karen White", email="karen.white@example.com", birthday=datetime(1982, 9, 19),
        #                    gender=False, address="707 Cherry Way", phone="5551234567")
        # profile8 = Profile(name="Liam Scott", email="liam.scott@example.com", birthday=datetime(1989, 3, 5),
        #                    gender=True, address="808 Ash Ct", phone="5556543210")
        # profile9 = Profile(name="Mia Clark", email="mia.clark@example.com", birthday=datetime(1994, 8, 22),
        #                    gender=False, address="909 Oak Pl", phone="5557890123")
        # profile10 = Profile(name="Nathan Adams", email="nathan.adams@example.com", birthday=datetime(1985, 5, 18),
        #                     gender=True, address="1010 Walnut St", phone="5558901234")
        #
        # # Thêm các hồ sơ vào session
        # db.session.add_all(
        #     [profile1, profile2, profile3, profile4, profile5, profile6, profile7, profile8, profile9, profile10])
        #
        # # Lưu thay đổi vào cơ sở dữ liệu
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
        # # Subjects
        # subject1 = Subject(name="Mathematics")
        # subject2 = Subject(name="Science")
        # subject3 = Subject(name="History")
        #
        # db.session.add_all([subject1, subject2, subject3])
        # db.session.commit()
        #
        # # Classes
        # classes = [
        #     Class(name="10a3", amount=25),
        #     Class(name="10a4", amount=25),
        #     Class(name="10a5", amount=25),
        #     Class(name="10a6", amount=25),
        #     Class(name="10a7", amount=25)
        # ]
        #
        # # Thêm tất cả các lớp vào cơ sở dữ liệu
        # db.session.add_all(classes)
        # db.session.commit()

        # # Students
        # student1 = Student(id=4, grade=Grade.K10)  # Profile ID 1
        # student2 = Student(id=5, grade=Grade.K11)  # Profile ID 2
        # student3 = Student(id=6, grade=Grade.K12)  # Profile ID 3
        # student4 = Student(id=7, grade=Grade.K10)  # Profile ID 4
        # student5 = Student(id=8, grade=Grade.K11)  # Profile ID 5
        # student6 = Student(id=9, grade=Grade.K12)  # Profile ID 6
        # student7 = Student(id=10, grade=Grade.K10)  # Profile ID 7
        #
        #
        # # Thêm các đối tượng Student vào cơ sở dữ liệu
        # db.session.add_all(
        #     [student1, student2, student3, student4, student5, student6, student7])
        #
        # db.session.commit()

        # # Tạo các đối tượng StudentClass để liên kết Student với các lớp học
        # student_class1 = StudentClass(class_id=1, student_id=4)  # Student ID 4
        # student_class2 = StudentClass(class_id=2, student_id=5)  # Student ID 5
        # student_class3 = StudentClass(class_id=3, student_id=6)  # Student ID 6
        # student_class4 = StudentClass(class_id=3, student_id=7)  # Student ID 7
        # student_class5 = StudentClass(class_id=4, student_id=8)  # Student ID 8
        # student_class6 = StudentClass(class_id=5, student_id=9)  # Student ID 9
        # student_class7 = StudentClass(class_id=1, student_id=10)  # Student ID 10
        #
        # # Thêm tất cả các bản ghi vào cơ sở dữ liệu
        # db.session.add_all([student_class1, student_class2, student_class3, student_class4, student_class5,
        #                     student_class6, student_class7])
        # db.session.commit()
        # # Semesters and Years
        # semester1 = Semester(name="First Semester")
        # semester2 = Semester(name="Second Semester")
        #
        # year1 = Year(name="2024-2025")
        #
        # db.session.add_all([semester1, semester2, year1])
        # db.session.commit()

        # # TeachingAssignments
        # teaching_assignment1 = TeachingAssignment(teacher_id=12, subjects_id=1,
        #                                           class_id=1, semester_id=1, years_id=1)
        # teaching_assignment2 = TeachingAssignment(teacher_id=12, subjects_id=1,
        #                                           class_id=2, semester_id=2, years_id=1)
        # teaching_assignment3 = TeachingAssignment(teacher_id=12, subjects_id=1,
        #                                           class_id=3, semester_id=2, years_id=1)
        # teaching_assignment4 = TeachingAssignment(teacher_id=12, subjects_id=1,
        #                                           class_id=4, semester_id=2, years_id=1)
        # teaching_assignment5 = TeachingAssignment(teacher_id=12, subjects_id=1,
        #                                           class_id=5, semester_id=2, years_id=1)
        # teaching_assignment6 = TeachingAssignment(teacher_id=12, subjects_id=1,
        #                                           class_id=1, semester_id=2, years_id=1)
        # teaching_assignment7 = TeachingAssignment(teacher_id=12, subjects_id=1,
        #                                           class_id=1, semester_id=2, years_id=1)
        # db.session.add_all([teaching_assignment1, teaching_assignment2, teaching_assignment3, teaching_assignment4, teaching_assignment5, teaching_assignment6, teaching_assignment7])
        # db.session.commit()

        # StaffClasses
        # staff_class1 = StaffClass(staff_id=1, class_id=1, time=datetime.now())
        # staff_class2 = StaffClass(staff_id=1, class_id=1, time=datetime.now())
        #
        # db.session.add_all([staff_class1, staff_class2])
        # db.session.commit()


        # Scores
        # score1 = Score(score=8.5, exam_type=ExamType.EXAM_FINAL, student_id=1, subject_id=1,
        #                semester_id=1, year_id=1)
        # score2 = Score(score=7.0, exam_type=ExamType.EXAM_45P, student_id=2, subject_id=1,
        #                semester_id=1, year_id=1)
        #
        # db.session.add_all([score1, score2])
        # db.session.commit()

        # Regulations
        # regulation1 = Regulation(type="General", name="Attendance Policy", min_value=75, max_value=100,
        #                          admin_id=3)
        #
        # db.session.add(regulation1)
        # db.session.commit()
