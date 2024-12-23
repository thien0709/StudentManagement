from manage_student import db
from manage_student.models import Score, Student, Subject, StudentClass, Class, Profile, TeachingAssignment

def get_students_by_filter(class_id=None, semester_id=None, subject_id=None, year_id=None):
    query = db.session.query(Student)

    if class_id:
        query = query.join(StudentClass, Student.id == StudentClass.student_id) \
            .join(Class, Class.id == StudentClass.class_id) \
            .filter(Class.id == class_id)

    if semester_id or year_id or subject_id:
        student_class_alias = db.aliased(StudentClass)
        query = query.join(student_class_alias, Student.id == student_class_alias.student_id) \
            .join(TeachingAssignment, student_class_alias.class_id == TeachingAssignment.class_id)
        if semester_id:
            query = query.filter(TeachingAssignment.semester_id == semester_id)
        if year_id:
            query = query.filter(TeachingAssignment.years_id == year_id)
        if subject_id:
            query = query.filter(TeachingAssignment.subjects_id == subject_id)


    print(query.statement.compile(dialect=db.engine.dialect))

    try:
        students = query.all()
        if not students:
            print("Không có học sinh nào thỏa mãn điều kiện.")
        return students
    except Exception as e:
        print(f"Lỗi khi truy vấn học sinh: {str(e)}")
        return []



# Lay danh sach sinh vien trong lop theo teaching assignment
def get_students_by_teaching(class_id=None, semester_id=None, year_id=None):
    try:
        query = db.session.query(Student).join(StudentClass, Student.id == StudentClass.student_id).join(Class, StudentClass.class_id == Class.id)
        if class_id:
            query = query.filter(Class.id == class_id)
        if semester_id or year_id:
            query = query.join(TeachingAssignment, TeachingAssignment.class_id == Class.id)
            if semester_id:
                query = query.filter(TeachingAssignment.semester_id == semester_id)
            if year_id:
                query = query.filter(TeachingAssignment.years_id == year_id)
        students = query.all()
        if not students:
            print("Không có học sinh nào thỏa mãn điều kiện.")
        return students

    except Exception as e:
        print(f"Lỗi khi truy vấn học sinh: {str(e)}")
        return []


def get_students_by_class(class_id, semester_id, year_id):
    return get_students_by_teaching(class_id=class_id, semester_id=semester_id, year_id=year_id)


def count_students_by_class(class_id=None):
    query = db.session.query(Student)
    if class_id:
        query = query.join(StudentClass).join(Class).filter(Class.id == class_id)
    return query.count()


def get_student_by_id(student_id):
    # Lấy học sinh từ cơ sở dữ liệu theo ID
    student = db.session.query(Student).filter_by(id=student_id).first()
    return student


def add_student(name, email, birthday, gender, address, phone, class_id, grade):
    profile = Profile(
        name=name,
        email=email,
        birthday=birthday,
        gender=gender,
        address=address,
        phone=phone
    )
    student = Student(
        grade=grade,
        profile=profile
    )

    db.session.add(student)
    db.session.commit()
    if class_id :
        studentclass = StudentClass(
            student_id=student.id,
            class_id=class_id
        )
        db.session.add(studentclass)
        db.session.commit()

    return student


def update_student( student_id, name, email, birthday, gender, address, phone):
    student = db.session.query(Student).filter_by(id=student_id).first()

    if student:
        student.profile.name = name
        student.profile.email = email
        student.profile.birthday = birthday
        student.profile.gender = gender
        student.profile.address = address
        student.profile.phone = phone
        db.session.commit()
        return student
    return None


def delete_student( student_id):
    # Tìm học sinh theo ID trong bảng Student
    student = db.session.query(Student).filter_by(id=student_id).first()

    if student:
        # Lấy profile_id từ student
        profile_id = student.profile.id

        # Xóa tất cả các điểm liên quan đến học sinh này
        db.session.query(Score).filter_by(student_id=student_id).delete()

        # Xóa tất cả các lớp liên quan đến học sinh này (cập nhật hoặc xóa các bản ghi trong bảng student_class)
        db.session.query(StudentClass).filter_by(student_id=student_id).delete()

        # Xóa bản ghi trong bảng Student
        db.session.delete(student)

        # Xóa bản ghi trong bảng Profile
        profile = db.session.query(Profile).filter_by(id=profile_id).first()
        if profile:
            db.session.delete(profile)


        db.session.commit()
        return True

    return False