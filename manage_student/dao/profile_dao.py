from datetime import datetime
from sqlalchemy.exc import IntegrityError
from manage_student.models import Profile
from manage_student import db


def add_profile(name, email, birthday, gender, address, phone):
    """
    Thêm một hồ sơ vào bảng Profile.
    :param name: Tên đầy đủ
    :param email: Email người dùng
    :param birthday: Ngày sinh (dạng datetime)
    :param gender: Giới tính (True: Nam, False: Nữ)
    :param address: Địa chỉ
    :param phone: Số điện thoại
    :return: True nếu thành công, ngược lại trả về lỗi
    """
    try:
        # Kiểm tra nếu gender là chuỗi "1" hoặc "0", chuyển thành Boolean
        gender = True if gender == "1" else False

        # Tạo đối tượng Profile
        new_profile = Profile(
            name=name,
            email=email,
            birthday=datetime.strptime(birthday, "%Y-%m-%d"),
            gender=gender,
            address=address,
            phone=phone,
        )

        # Thêm vào cơ sở dữ liệu
        db.session.add(new_profile)
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return {"status": "error", "message": "Email hoặc số điện thoại đã tồn tại!"}
    except Exception as e:
        db.session.rollback()
        return {"status": "error", "message": str(e)}
