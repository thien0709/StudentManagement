from manage_student.models import User, UserRole, Profile, Teacher, Staff, Admin
from manage_student import app, db
import hashlib
import cloudinary.uploader


def auth_user(username, password):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    return User.query.filter(User.username.__eq__(username),
                             User.password.__eq__(password)).first()


# auth_dao.py (or wherever your add_user function is located)





def get_user_by_id(id):
    return User.query.get(id)

def get_user_by_username(username):
    user = db.session.query(User).filter_by(username=username).first()
    return user

def add_user(username, email, role, password, avatar=None, name=None, birthday=None, gender=None, address=None, phone=None):
    # Tạo đối tượng Profile
    profile = Profile(
        name=name,
        email=email,
        birthday=birthday,
        gender=gender,
        address=address,
        phone=phone
    )

    # Mã hóa mật khẩu
    hashed_password = hashlib.md5(password.encode('utf-8')).hexdigest()

    # Tải lên avatar nếu có
    avatar_url = None
    if avatar:
        try:
            res = cloudinary.uploader.upload(avatar)
            avatar_url = res.get('secure_url')
        except Exception as e:
            print(f"Error uploading avatar: {e}")

    # Tạo đối tượng User và liên kết với Profile
    user = User(
        username=username,
        password=hashed_password,
        role=role,
        avatar=avatar_url if avatar_url else User.avatar.default,
        profile=profile
    )

    try:
        db.session.add(user)
        db.session.flush()

        if role == UserRole.ADMIN:
            admin = Admin(user=user)
            db.session.add(admin)
        elif role == UserRole.STAFF:
            staff = Staff(user=user)
            db.session.add(staff)
        elif role == UserRole.TEACHER:
            teacher = Teacher(user=user)
            db.session.add(teacher)

        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()
        print(f"Error adding user: {e}")
        return None


#
# def add_user(name, username, password, avatar=None):
#
#
#     u = User(name=name, username=username, password=password)
#
#     if avatar:
#         res = cloudinary.uploader.upload(avatar)
#         u.avatar = res.get('secure_url')
#
#     db.session.add(u)
#     db.session.commit()
#
#     def add_user(username, email, password, avatar=None):
#         # Logic to add the user to the database
#         # Ensure that your database model supports the 'email' field
#         new_user = User(username=username, email=email, password=password, avatar=avatar)
#
#         try:
#             db.session.add(new_user)
#             db.session.commit()
#             return new_user
#         except Exception as e:
#             db.session.rollback()
#             print(f"Error adding user: {e}")
#             return None