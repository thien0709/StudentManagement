from manage_student import db
from manage_student.models import Score, Student, Subject, StudentClass, Class, Profile, TeachingAssignment

def get_students_by_filter(class_id=None, semester_id=None, subject_id=None, year_id=None):
    query = db.session.query(Student)

    query = query.join(StudentClass, Student.id == StudentClass.student_id) \
            .join(Class, Class.id == StudentClass.class_id)
    if class_id:
        query = query.filter(Class.id == class_id)

    query = query.join(TeachingAssignment, TeachingAssignment.class_id == Class.id)
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
        return



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
        return


def get_students_by_class1(class_id, semester_id, year_id):
    return get_students_by_teaching(class_id=class_id, semester_id=semester_id, year_id=year_id)

def get_students_by_class(class_id, year_id):
    return (
        db.session.query(Student)
        .join(StudentClass, Student.id == StudentClass.student_id)
        .join(Class, StudentClass.class_id == Class.id)
        .filter(Class.id == class_id, Class.year_id == year_id)
        .all()
    )



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


def update_student(student_id, name, email, birthday, gender, address, phone, grade):
    student = db.session.query(Student).filter_by(id=student_id).first()

    if student:
        student.profile.name = name
        student.profile.email = email
        student.profile.birthday = birthday
        student.profile.gender = gender
        student.profile.address = address
        student.profile.phone = phone
        student.grade = grade

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

def remove_student_from_class(student_id, class_id):
    try:
        # Tìm bản ghi trong bảng StudentClass dựa trên student_id và class_id
        student_class_entry = db.session.query(StudentClass).filter_by(student_id=student_id, class_id=class_id).first()

        if not student_class_entry:
            print("Học sinh không có trong lớp.")
            return False

        # Xóa bản ghi StudentClass
        db.session.delete(student_class_entry)
        db.session.commit()

        print("Xóa học sinh khỏi lớp thành công.")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi xóa học sinh khỏi lớp: {str(e)}")
        return False

def get_students_without_class():
    try:
        # Truy vấn các học sinh không có lớp, sử dụng LEFT OUTER JOIN
        students_without_class = db.session.query(Student).outerjoin(StudentClass, Student.id == StudentClass.student_id) \
            .filter(StudentClass.student_id == None).all()

        if not students_without_class:
            print("Không có học sinh nào chưa có lớp.")
        return students_without_class

    except Exception as e:
        print(f"Lỗi khi truy vấn học sinh chưa có lớp: {str(e)}")
        return []


def add_student_to_class(student_id, class_id):
    try:
        student = db.session.query(Student).filter_by(id=student_id).first()

        if not student:
            print("Học sinh không tồn tại.")
            return False

        class_instance = db.session.query(Class).filter_by(id=class_id).first()

        if not class_instance:
            print("Lớp học không tồn tại.")
            return False

        # Kiểm tra grade của học sinh và lớp có khớp không
        if student.grade != class_instance.grade:
            print(f"Grade của học sinh ({student.grade}) không khớp với grade của lớp ({class_instance.grade}).")
            return False

        existing_entry = db.session.query(StudentClass).filter_by(student_id=student_id, class_id=class_id).first()

        if existing_entry:
            print("Học sinh đã có trong lớp.")
            return False

        new_student_class = StudentClass(student_id=student_id, class_id=class_id)
        db.session.add(new_student_class)
        db.session.commit()

        print("Thêm học sinh vào lớp thành công.")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi thêm học sinh vào lớp: {str(e)}")
        return False


