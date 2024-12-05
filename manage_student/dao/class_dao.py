from manage_student import db
from manage_student.models import Student, Score, Subject, Semester, Class, Year, StudentClass
from sqlalchemy.orm import aliased


# Hàm lấy tất cả các lớp học
def get_classes():
    try:
        classes = db.session.query(Class).all()
        if not classes:
            print("Không có lớp học trong cơ sở dữ liệu.")
        return classes
    except Exception as e:
        print(f"Lỗi khi truy vấn lớp học: {str(e)}")
        return []


# Hàm lấy tất cả các môn học
def get_subjects():
    try:
        return db.session.query(Subject).all()
    except Exception as e:
        print(f"Lỗi khi truy vấn môn học: {str(e)}")
        return []


# Hàm lấy tất cả các học kỳ
def get_semesters():
    try:
        semesters = db.session.query(Semester).all()
        if not semesters:
            print("Không có học kỳ trong cơ sở dữ liệu.")
        return semesters
    except Exception as e:
        print(f"Lỗi khi truy vấn học kỳ: {str(e)}")
        return []


# Hàm lấy tất cả các năm học
def get_years():
    try:
        return db.session.query(Year).all()
    except Exception as e:
        print(f"Lỗi khi truy vấn năm học: {str(e)}")
        return []


def get_students_by_filter(class_id=None, semester_id=None, subject_id=None, year_id=None):
    query = db.session.query(Student)

    # Kết nối với bảng Students_Classes và Class
    if class_id:
        query = query.join(StudentClass).join(Class).filter(Class.id == class_id)

    # Kết nối với bảng Score nếu có môn học hoặc học kỳ
    if subject_id:
        query = query.join(Score).filter(Score.subject_id == subject_id)

    if semester_id:
        query = query.join(Semester).filter(Semester.id == semester_id)

    if year_id:
        query = query.join(Year).filter(Year.id == year_id)

    try:
        students = query.all()
        if not students:
            print("Không có học sinh nào thỏa mãn điều kiện.")
        return students
    except Exception as e:
        print(f"Lỗi khi truy vấn học sinh: {str(e)}")
        return []
