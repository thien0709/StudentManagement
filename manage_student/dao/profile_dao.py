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
