
from manage_student.dao import regulation_dao, student_dao
from manage_student.models import Student, Score, Subject, Semester, Class, Year, StudentClass, TeachingAssignment, \
    Grade
from sqlalchemy.orm import aliased


from manage_student import db
from manage_student.models import Class

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


# Hàm lấy tên lớp học theo ID
def get_class_name(class_id):
    try:
        class_ = db.session.query(Class).get(class_id)
        return class_.name if class_ else None
    except Exception as e:
        print(f"Lỗi khi truy vấn tên lớp học: {str(e)}")
        return None
def assign_students_to_classes():
    # Lấy danh sách học sinh chưa được phân lớp
    unassigned_students = Student.query.filter(~Student.classes.any()).all()

def get_classes_by_grade(grade):
    if grade:
        return Class.query.filter_by(grade=Grade[grade]).all()
    return Class.query.all()

def assign_students_to_classes():
    unassigned_students = student_dao.get_students_without_class()
    classes = Class.query.all()
    print(classes)

    for student in unassigned_students:
        assigned = False

        # Lặp qua các lớp để tìm lớp phù hợp
        for class_ in classes:
            # Kiểm tra grade của học sinh và lớp
            if class_.grade == student.grade and class_.amount < regulation_dao.get_max_students_in_class():
                student_class = StudentClass(class_id=class_.id, student_id=student.id)
                db.session.add(student_class)
                class_.amount += 1
                assigned = True
                break

        if not assigned:
            # Lọc các lớp cùng khối (grade) của học sinh
            classes_in_grade = [class_ for class_ in classes if class_.grade == student.grade]

            # Đếm số lớp cùng khối và tạo lớp mới
            new_class_name = f"{student.grade.value}a{len(classes_in_grade) + 1}"

            # Tạo lớp mới và gán học sinh vào
            new_class = Class(name=new_class_name, amount=1, grade=student.grade, year_id= Year.query.first().id)
            db.session.add(new_class)
            db.session.commit()

            student_class = StudentClass(class_id=new_class.id, student_id=student.id)
            db.session.add(student_class)
            classes.append(new_class)
    db.session.commit()  # Lưu các thay đổi vào cơ sở dữ liệu


def delete_class(class_id):
    cls = Class.query.get(class_id)
    if cls:
        grade_count = Class.query.filter_by(grade=cls.grade).count()
        if grade_count <= regulation_dao.get_min_class_in_grade():
            raise ValueError("Không thể xóa lớp này vì khối phải có tối thiểu 1 lớp!")

        # Xóa các liên kết với StudentClass
        student_classes = StudentClass.query.filter_by(class_id=class_id).all()
        for student_class in student_classes:
            db.session.delete(student_class)
        db.session.commit()

        # Xóa tất cả các TeachingAssignment liên quan
        assignments = TeachingAssignment.query.filter_by(class_id=class_id).all()
        for assignment in assignments:
            db.session.delete(assignment)
        db.session.commit()

        # Xóa lớp
        db.session.delete(cls)
        db.session.commit()
        return True
    else:
        raise ValueError("Class không tồn tại!")
