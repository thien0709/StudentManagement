from manage_student import db
from manage_student.models import Profile, Student, StudentClass


def add_profile(name, email, birthday, gender, address, phone):
    # Chuyển đổi gender từ chuỗi thành Boolean
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

    student = Student(
        profile=profile
    )
    db.session.add(student)
    db.session.commit()
    return profile
