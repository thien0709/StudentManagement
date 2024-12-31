from manage_student import db
from manage_student.models import Profile, Student, Grade


def add_profile(name, email, birthday, gender, address, phone, grade):
    print("Adding profile...")

    # Kiểm tra trùng lặp email và số điện thoại trước khi thêm
    duplicate_check = check_duplicate_profile(email, phone)
    if duplicate_check['status'] == 'duplicate':
        return {"status": "error", "message": "Email hoặc số điện thoại đã tồn tại trong hệ thống."}

    try:
        gender_bool = True if gender == '1' else False

        # Tạo đối tượng Profile
        profile = Profile(
            name=name,
            email=email,
            birthday=birthday,
            gender=gender_bool,
            address=address,
            phone=phone
        )
        db.session.add(profile)
        db.session.commit()  # Commit để lưu Profile vào cơ sở dữ liệu
        print("Profile added successfully.")

        # Kiểm tra xem grade có phải là chuỗi và chuyển đổi nếu cần
        if isinstance(grade, str):
            # Chuyển grade từ chuỗi thành giá trị Enum
            grade = Grade[grade]  # Ví dụ: 'K10' -> Grade.K10

        # Tạo đối tượng Student (sử dụng thông tin Profile và thêm grade)
        student = Student(profile=profile, grade=grade)  # Kết nối Profile và Student, và thêm grade
        db.session.add(student)
        db.session.commit()
        print("Student added successfully.")

        return {"status": "success", "message": "Hồ sơ học sinh đã được thêm thành công!"}
    except Exception as e:
        print(f"Error while adding profile: {e}")
        db.session.rollback()
        return {"status": "error", "message": f"Đã xảy ra lỗi: {str(e)}"}


def check_duplicate_profile(email, phone):
    """
    Kiểm tra xem email và số điện thoại có trùng lặp trong cơ sở dữ liệu không.
    Trả về một dictionary chứa thông tin trùng lặp.
    """
    student_by_email = Profile.query.filter_by(email=email).first()
    student_by_phone = Profile.query.filter_by(phone=phone).first()

    if student_by_email and student_by_phone:
        return {'status': 'duplicate', 'duplicateEmail': True, 'duplicatePhone': True}
    elif student_by_email:
        return {'status': 'duplicate', 'duplicateEmail': True}
    elif student_by_phone:
        return {'status': 'duplicate', 'duplicatePhone': True}

    return {'status': 'ok'}
