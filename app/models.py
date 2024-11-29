from app import db

# Bảng lớp học
class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

# Bảng học sinh
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))

# Bảng môn học
class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

# Bảng học kỳ
class Semester(db.Model):
    __tablename__ = 'semesters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

# Bảng năm học
class Year(db.Model):
    __tablename__ = 'years'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

# Bảng điểm
class Score(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id'))
    year_id = db.Column(db.Integer, db.ForeignKey('years.id'))
    score_15_min = db.Column(db.String(255))  # Lưu danh sách điểm dưới dạng chuỗi
    score_1_hour = db.Column(db.String(255))  # Lưu danh sách điểm dưới dạng chuỗi
    final_exam = db.Column(db.Float)
    # Generated column: chỉ đọc, không ghi giá trị
    average_score = db.Column(db.Float, nullable=True, default=None)
