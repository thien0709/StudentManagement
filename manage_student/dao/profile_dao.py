from datetime import datetime
from sqlalchemy.exc import IntegrityError
from manage_student.models import Profile, Student, StudentClass
from manage_student import db


def add_profile(name, email, birthday, gender, address, phone, class_id=None, grade="K10"):
    # Tạo đối tượng Profile
    profile = Profile(
        name=name,
        email=email,
        birthday=birthday,
        gender=gender,
        address=address,
        phone=phone
    )

    # Thêm Profile vào cơ sở dữ liệu
    db.session.add(profile)
    db.session.commit()  # Commit để Profile có ID

    # Tạo đối tượng Student và liên kết với Profile
    student = Student(
        grade=grade,
        profile=profile
    )

    # Thêm Student vào cơ sở dữ liệu
    db.session.add(student)
    db.session.commit()  # Commit để lưu Student

    # Nếu có class_id, tạo đối tượng StudentClass để liên kết với lớp học
    if class_id:
        studentclass = StudentClass(
            student_id=student.id,
            class_id=class_id
        )
        db.session.add(studentclass)
        db.session.commit()  # Commit để lưu StudentClass

    return student
