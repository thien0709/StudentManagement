from manage_student import db
from manage_student.models import Class, Grade, Student, StudentClass
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


def get_grades():
    return [grade.name for grade in Grade]


def get_classes_by_grade(grade):
    # Ví dụ sử dụng SQLAlchemy để lấy danh sách lớp theo khối
    return Class.query.filter_by(grade=grade).all()

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

    # Lấy danh sách các lớp hiện có
    classes = Class.query.all()

    for student in unassigned_students:
        assigned = False

        # Tìm lớp có chỗ trống
        for class_ in classes:
            if class_.amount < 30:  # Giả sử mỗi lớp tối đa 30 học sinh
                # Thêm học sinh vào lớp
                student_class = StudentClass(class_id=class_.id, student_id=student.id)
                db.session.add(student_class)

                # Cập nhật số lượng học sinh trong lớp
                class_.amount += 1
                assigned = True
                break

        # Nếu không có lớp nào đủ chỗ, tạo lớp mới
        if not assigned:
            new_class = Class(name=f"Class {len(classes) + 1}", amount=1)
            db.session.add(new_class)
            db.session.commit()  # Lưu lớp mới vào DB

            # Thêm học sinh vào lớp mới
            student_class = StudentClass(class_id=new_class.id, student_id=student.id)
            db.session.add(student_class)

            # Thêm lớp mới vào danh sách lớp
            classes.append(new_class)

    db.session.commit()  # Lưu tất cả thay đổi vào DB
