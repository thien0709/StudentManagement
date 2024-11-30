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
    id = Column(Integer, ForeignKey(Profile.id), primary_key=True, nullable=False, unique=True)
    username = Column(String(50), unique=True)
    password = Column(String(50))
    avatar = Column(String(200), default='https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg')
    user_role = Column(Enum(UserRole))
    profile = relationship("Profile", backref="user", lazy=True)


class Staff(db.Model):
    id = Column(Integer, ForeignKey(User.id), primary_key=True, unique=True, nullable=False)
    user = relationship("User", backref="staff", lazy=True)


class Teacher(db.Model):
    id = Column(Integer, ForeignKey(User.id), primary_key=True, unique=True, nullable=False)
    class_teach = relationship("Class", backref="teacher", lazy=True)
    user = relationship("User", backref="teacher", lazy=True)

class Subject(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    grade = Column(Enum(GRADE))
    number_of_15p = Column(Integer)
    number_of_45p = Column(Integer)


class Class(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    grade = Column(Enum(GRADE))
    count = Column(Integer)
    amount = Column(Integer, default=0)
    year = Column(Integer, default=datetime.now().year)
    teacher_id = Column(Integer, ForeignKey(Teacher.id))
    students = relationship("Students_Classes", backref="class", lazy=True)

class Student(db.Model):
    id = Column(Integer, ForeignKey(Profile.id), primary_key=True, unique=True)
    grade = Column(Enum(GRADE), default=GRADE.K10)
    classes = relationship("Students_Classes", backref="student", lazy=True)
    profile = relationship("Profile", backref="student", lazy=True)

class Students_Classes(db.Model):
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    class_id = Column(Integer, ForeignKey(Class.id), nullable=False)
    student_id = Column(Integer, ForeignKey(Student.id), nullable=False)


class Teachers_Subject(db.Model):
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey(Teacher.id), nullable=False)
    subject_id = Column(Integer, ForeignKey(Subject.id), nullable=False)

    teacher = relationship("Teacher", backref="teachers_subject", lazy=True)
    subject = relationship("Subject", backref="subject_teacher", lazy=True)

class Semester(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    semester_name = Column(String(50))


class Teaching_plan(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    score_deadline = Column(DateTime)
    class_id = Column(Integer, ForeignKey(Class.id), nullable=False)
    semester_id = Column(Integer, ForeignKey(Semester.id), nullable=False)
    teacher_subject_id = Column(Integer, ForeignKey(Teachers_Subject.id), nullable=False)

    teacher_subject = relationship("Teachers_Subject", backref="teaching_plan")
    # subject_id = Column(Integer, ForeignKey(Subject.id), nullable=False)
    # teacher_id = Column(Integer, ForeignKey(Teacher.id), nullable=False)

    # teacher = relationship("Teacher", backref="teacher", lazy=True)
    semester = relationship("Semester", backref="semester", lazy=True)
    class_teach = relationship("Class", backref="teach", lazy=True)
    # subject = relationship("Subject", backref="subject", lazy=True)


class Exam(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey(Student.id), nullable=False)
    teach_plan_id = Column(Integer, ForeignKey(Teaching_plan.id), nullable=False)
    scores = relationship("Score", backref="exam", lazy=True)

    student = relationship("Student", backref="exam", lazy=True)
    teach_plan = relationship("Teaching_plan", backref="exam", lazy=True)


class Score(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    score = Column(Float)
    type = Column(Enum(TypeExam))
    count = Column(Integer)
    Exam_id = Column(Integer, ForeignKey(Exam.id), nullable=False)

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


if __name__ == '__main__':
    with app.app_context():
        # pass
        db.create_all()
        p1 = Profile(name="Bach Xuan Thien")
        p2 = Profile(name="Dang Hoang Danh")
        p3 = Profile(name="Duong Vo Duy Khang")
        db.session.add_all([p1, p2, p3])
        db.session.commit()
        acc1 = User(id=p1.id, username="admin", password=str(hashlib.md5("123".encode("utf-8")).hexdigest()), user_role=UserRole.ADMIN)
        acc2 = User(id=p2.id, username="teacher", password=str(hashlib.md5("123".encode("utf-8")).hexdigest()), user_role=UserRole.TEACHER)
        acc3 = User(id=p3.id, username="staff", password=str(hashlib.md5("123".encode("utf-8")).hexdigest()), user_role=UserRole.STAFF)
        db.session.add_all([acc1, acc2, acc3])
        db.session.commit()
        # cl101 = Class(grade=GRADE.K10, count=1, amount=10, teacher_id=teacher.id)
        # cl102 = Class(grade=GRADE.K10, count=2, amount=11, teacher_id=teacher.id)
        # cl103 = Class(grade=GRADE.K10, count=3, amount=12, teacher_id=teacher.id)
        # cl111 = Class(grade=GRADE.K11, count=1, amount=7, teacher_id=teacher.id)
        # cl112 = Class(grade=GRADE.K11, count=2, amount=8, teacher_id=teacher.id)
        # cl113 = Class(grade=GRADE.K11, count=3, amount=9, teacher_id=teacher.id)
        # cl121 = Class(grade=GRADE.K12, count=1, amount=1, teacher_id=teacher.id)
        # cl122 = Class(grade=GRADE.K12, count=2, amount=2, teacher_id=teacher.id)
        # cl123 = Class(grade=GRADE.K12, count=3, amount=3, teacher_id=teacher.id)
        # db.session.add_all([cl101, cl102, cl103, cl111, cl112, cl113, cl121, cl122, cl123])
        # db.session.commit()
        #
        # subjects = [
        #     Subject(name='Toán', grade=GRADE.K10, number_of_15p=3, number_of_45p=3),
        #     Subject(name='Lý', grade=GRADE.K10, number_of_15p=3, number_of_45p=2),
        #     Subject(name='Hóa', grade=GRADE.K10, number_of_15p=2, number_of_45p=2),
        #     Subject(name='Sinh', grade=GRADE.K10, number_of_15p=2, number_of_45p=1),
        #
        #     Subject(name='Toán', grade=GRADE.K11, number_of_15p=3, number_of_45p=3),
        #     Subject(name='Lý', grade=GRADE.K11, number_of_15p=3, number_of_45p=2),
        #     Subject(name='Hóa', grade=GRADE.K11, number_of_15p=2, number_of_45p=2),
        #     Subject(name='Sinh', grade=GRADE.K11, number_of_15p=2, number_of_45p=1),
        #     Subject(name='Văn', grade=GRADE.K11, number_of_15p=2, number_of_45p=1),
        #
        #     Subject(name='Toán', grade=GRADE.K12, number_of_15p=3, number_of_45p=3),
        #     Subject(name='Lý', grade=GRADE.K12, number_of_15p=3, number_of_45p=2),
        #     Subject(name='Hóa', grade=GRADE.K12, number_of_15p=2, number_of_45p=2),
        #     Subject(name='Sinh', grade=GRADE.K12, number_of_15p=2, number_of_45p=1),
        #     Subject(name='Sử', grade=GRADE.K12, number_of_15p=2, number_of_45p=1),
        # ]
        # for subject in subjects:
        #     db.session.add(subject)
        # db.session.commit()
        #
        # p4 = Profile(name="Giáo Viên toán 10 11 12 A")
        # p5 = Profile(name="Giáo Viên lý 10 11 12 B")
        # p6 = Profile(name="Giáo Viên hóa 10 11 12C")
        # p7 = Profile(name="Giáo Viên sinh 10 11 12 D")
        # p8 = Profile(name="Giáo Viên văn 11 E")
        # p9 = Profile(name="Giáo Viên sử 12 F")
        # db.session.add_all([p4, p5, p6, p7, p8, p9])
        # db.session.commit()
        #
        # acc4 = User(id=p4.id, username="gv4", password=str(hashlib.md5("123".encode("utf-8")).hexdigest()),
        #             user_role=UserRole.TEACHER)
        # acc5 = User(id=p5.id, username="gv5", password=str(hashlib.md5("123".encode("utf-8")).hexdigest()),
        #             user_role=UserRole.TEACHER)
        # acc6 = User(id=p6.id, username="gv6", password=str(hashlib.md5("123".encode("utf-8")).hexdigest()),
        #             user_role=UserRole.TEACHER)
        # acc7 = User(id=p7.id, username="gv7", password=str(hashlib.md5("123".encode("utf-8")).hexdigest()),
        #             user_role=UserRole.TEACHER)
        # acc8 = User(id=p8.id, username="gv8", password=str(hashlib.md5("123".encode("utf-8")).hexdigest()),
        #             user_role=UserRole.TEACHER)
        # acc9 = User(id=p9.id, username="gv9", password=str(hashlib.md5("123".encode("utf-8")).hexdigest()),
        #             user_role=UserRole.TEACHER)
        # db.session.add_all([acc4, acc5, acc6, acc7, acc8, acc9])
        # db.session.commit()
        #
        # teacher4 = Teacher(id=acc4.id, title=Title.BACHELOR)
        # teacher5 = Teacher(id=acc5.id, title=Title.BACHELOR)
        # teacher6 = Teacher(id=acc6.id, title=Title.BACHELOR)
        # teacher7 = Teacher(id=acc7.id, title=Title.BACHELOR)
        # teacher8 = Teacher(id=acc8.id, title=Title.BACHELOR)
        # teacher9 = Teacher(id=acc9.id, title=Title.BACHELOR)
        # db.session.add_all([teacher4, teacher5, teacher6, teacher7, teacher8, teacher9])
        # db.session.commit()
        # #
        # teacher_subject = [
        #     Teachers_Subject(teacher_id=teacher4.id, subject_id=subjects[0].id),
        #     Teachers_Subject(teacher_id=teacher4.id, subject_id=subjects[4].id),
        #     Teachers_Subject(teacher_id=teacher4.id, subject_id=subjects[9].id),
        #
        #     Teachers_Subject(teacher_id=teacher5.id, subject_id=subjects[1].id),
        #     Teachers_Subject(teacher_id=teacher5.id, subject_id=subjects[5].id),
        #     Teachers_Subject(teacher_id=teacher5.id, subject_id=subjects[10].id),
        #
        #     Teachers_Subject(teacher_id=teacher6.id, subject_id=subjects[2].id),
        #     Teachers_Subject(teacher_id=teacher6.id, subject_id=subjects[6].id),
        #     Teachers_Subject(teacher_id=teacher6.id, subject_id=subjects[11].id),
        #
        #     Teachers_Subject(teacher_id=teacher7.id, subject_id=subjects[3].id),
        #     Teachers_Subject(teacher_id=teacher7.id, subject_id=subjects[7].id),
        #     Teachers_Subject(teacher_id=teacher7.id, subject_id=subjects[12].id),
        #
        #     Teachers_Subject(teacher_id=teacher8.id, subject_id=subjects[9].id),
        #     Teachers_Subject(teacher_id=teacher9.id, subject_id=subjects[13].id),
        # ]
        #
        # for ts in teacher_subject:
        #     db.session.add(ts)
        # db.session.commit()
        #
        # semesters = [
        #     Semester(semester_name="Học kì 1"),
        #     Semester(semester_name="Học kì 2"),
        # ]
        # for s in semesters:
        #     db.session.add(s)
        # db.session.commit()
        #

        # regulations = [
        #     Regulation(type="student", regulation_name="Tiếp nhận học sinh", min=6, max=18),
        #     Regulation(type="amount", regulation_name="Sĩ số tối đa", min=0, max=30),
        #
        # ]
        # for r in regulations:
        #     db.session.add(r)
        # db.session.commit()

        # for i in range(3):
        #     profile = Profile(name="student " + str(i), email="2151013030hung@ou.edu.vn", birthday=datetime.now(),phone=str(1000000000+i),gender=0,address="chossh")
        #     db.session.add(profile)
        #     db.session.commit()
        #     stu = Student(id=profile.id)
        #     db.session.add(stu)
        #     db.session.commit()

        # profiles_data = [
        #     {"id": 5, "name": "Trần Lưu Quốc Tuấn", "email": "john@example.com", "dob": "2003-01-15", "gender": True,
        #      "address": "123 Main St", "phone": "1234567890"},
        #     {"id": 6, "name": "Nguyễn Thế Anh", "email": "jane@example.com", "dob": "2003-05-20", "gender": False,
        #      "address": "456 Elm St", "phone": "9876543210"},
        #     # Thêm thông tin hồ sơ cho sinh viên khác nếu cần
        # ]
        # for profile_info in profiles_data:
        #     profile = Profile(**profile_info)
        #     db.session.add(profile)
        #
        # # db.session.commit()
        #
        #     # Thêm sinh viên khác nếu cần
        # ]
        # #
        # for student_info in students_data:
        #     student = Student(**student_info)
        #     db.session.add(student)
        #
        # db.session.commit()
        # #
        # student_class = Students_Classes(class_id = 4,student_id = 8)
        # student_class1 = Students_Classes(class_id = 4,student_id = 9)
        # student_class2 = Students_Classes(class_id = 4,student_id = 10)
        # student_class3 = Students_Classes(class_id = 4,student_id = 11)
        # db.session.add_all([student_class,student_class1,student_class2,student_class3])
        # db.session.commit()