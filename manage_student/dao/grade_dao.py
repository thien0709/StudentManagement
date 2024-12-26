from flask import jsonify
from manage_student import db
from manage_student.dao.score_dao import count_students_passed, logger
from manage_student.models import Grade, Class


def api_get_grades():
    try:
        # Lấy tất cả tên của các giá trị trong Enum Grade
        grades = [grade.name for grade in Grade]
        # Trả về danh sách khối học dưới dạng JSON
        return jsonify(grades)
    except Exception as e:
        # Nếu có lỗi, trả về thông báo lỗi
        return jsonify({"error": f"Lỗi khi lấy khối: {str(e)}"}), 500


def api_get_classes_by_grade(grade_name):
    try:
        # Kiểm tra xem grade_name có phải là một giá trị hợp lệ trong Enum không
        if grade_name not in [grade.name for grade in Grade]:
            return jsonify({"error": "Khối học không hợp lệ"}), 400

        # Lấy giá trị Enum từ tên grade_name
        grade_enum_value = Grade[grade_name]  # Đây là biến của Enum, như Grade.GRADE_1

        # Lấy các lớp học từ cơ sở dữ liệu tương ứng với giá trị grade_enum_value
        classes = Class.query.filter_by(grade=grade_enum_value).all()

        # Chuyển đổi các lớp học thành dạng JSON
        class_data = [{"id": c.id, "name": c.name} for c in classes]
        return jsonify(class_data)
    except Exception as e:
        return jsonify({"error": f"Lỗi khi lấy lớp: {str(e)}"}), 500





def api_get_class_amount(class_id):
    try:
        # Truy vấn lớp học theo class_id
        class_data = db.session.query(Class).get(class_id)
        if class_data:
            return jsonify({"amount": class_data.amount})
        else:
            return jsonify({"error": "Không tìm thấy lớp"}), 404
    except Exception as e:
        # Xử lý lỗi và trả về thông báo
        return jsonify({"error": f"Lỗi khi lấy sĩ số: {str(e)}"}), 500


def api_get_passed_count(class_id, subject_id, semester_id, year_id):
    try:
        # Giả sử bạn có một cách để tính số học sinh đạt yêu cầu
        # Ví dụ: count_students_passed là một hàm tính số học sinh đạt yêu cầu (điểm >= 5)

        passed_count = count_students_passed(class_id, subject_id, semester_id, year_id)
        return jsonify({'passed_count': passed_count})
    except Exception as e:
        # Log lỗi và trả về thông báo lỗi
        logger.error(f"Error in /get_passed_count: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500