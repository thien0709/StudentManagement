from manage_student import db
from manage_student.models import Profile, Student, StudentClass


def add_profile(name, email, birthday, gender, address, phone):
    print("Adding profile...")
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
        db.session.commit()
        print("Profile added successfully.")

        student = Student(profile=profile)
        db.session.add(student)
        db.session.commit()
        print("Student added successfully.")

        return profile
    except Exception as e:
        print(f"Error while adding profile: {e}")
        db.session.rollback()
        return None


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