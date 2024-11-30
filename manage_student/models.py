from enum import unique

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from manage_student import db, app


# Bảng lớp học
class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False,unique=True)
    students = db.relationship('Student', back_populates='classroom', lazy=True)


# Bảng học sinh
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    classroom = db.relationship('Class', back_populates='students')
    scores = db.relationship('Score', back_populates='student', lazy=True)


# Bảng môn học
class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    scores = db.relationship('Score', back_populates='subject', lazy=True)


# Bảng học kỳ
class Semester(db.Model):
    __tablename__ = 'semesters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    scores = db.relationship('Score', back_populates='semester', lazy=True)


# Bảng năm học
class Year(db.Model):
    __tablename__ = 'years'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    scores = db.relationship('Score', back_populates='year', lazy=True)


# Bảng điểm số
class Score(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Float, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    student = db.relationship('Student', back_populates='scores')
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    subject = db.relationship('Subject', back_populates='scores')
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id'), nullable=False)
    semester = db.relationship('Semester', back_populates='scores')
    year_id = db.Column(db.Integer, db.ForeignKey('years.id'), nullable=False)
    year = db.relationship('Year', back_populates='scores')


# Tạo dữ liệu đầy đủ
def create_full_sample_data():
    # Tạo lớp học
    class_1 = Class(name='Class 1')
    class_2 = Class(name='Class 2')

    # Tạo môn học
    subject_math = Subject(name="Mathematics")
    subject_science = Subject(name="Science")
    subject_literature = Subject(name="Literature")

    # Tạo học kỳ
    semester_1 = Semester(name="Semester 1")
    semester_2 = Semester(name="Semester 2")

    # Tạo năm học
    year_1 = Year(name="Year 2023-2024")
    year_2 = Year(name="Year 2024-2025")

    # Tạo học sinh và điểm
    student_1 = Student(name="Student A", classroom=class_1)
    student_2 = Student(name="Student B", classroom=class_1)
    student_3 = Student(name="Student C", classroom=class_1)
    student_4 = Student(name="Student D", classroom=class_2)
    student_5 = Student(name="Student E", classroom=class_2)
    student_6 = Student(name="Student F", classroom=class_2)
    student_7 = Student(name="Student G", classroom=class_1)
    student_8 = Student(name="Student H", classroom=class_1)
    student_9 = Student(name="Student I", classroom=class_2)
    student_10 = Student(name="Student J", classroom=class_2)


    # Thêm dữ liệu vào cơ sở dữ liệu
    db.session.add_all([class_1, class_2, subject_math, subject_science, subject_literature, semester_1, semester_2, year_1, year_2] )
    db.session.add_all([student_1, student_2])
    try:
        db.session.commit()
        print("Dữ liệu đã được thêm vào cơ sở dữ liệu.")
    except Exception as e:
        db.session.rollback()
        print(f"Đã xảy ra lỗi khi commit dữ liệu: {e}")


# Đảm bảo khi chạy script sẽ tạo dữ liệu mẫu
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_full_sample_data()

    print("Sample data has been created!")
