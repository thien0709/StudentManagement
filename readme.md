# Quản Lý Sinh Viên

Hệ thống "Quản Lý Sinh Viên" là một phần mềm được phát triển để hỗ trợ việc quản lý thông tin và hoạt động học tập của học sinh trong nhà trường.

## Chức năng chính

- **Tiếp nhận học sinh mới**
- **Lập và quản lý danh sách lớp**
- **Nhập và xuất điểm số**
- **Thống kê và báo cáo kết quả học tập bằng biểu đồ**
- **Phân quyền truy cập theo vai trò**: Quản trị viên, nhân viên, giáo viên.
- **Tùy chỉnh quy định**: Độ tuổi tiếp nhận, sĩ số lớp học, cột điểm, môn học.

## Kiến trúc hệ thống

Hệ thống sử dụng kiến trúc **MVT (Model - View - Template)**:

- **Model**: Định nghĩa bảng cơ sở dữ liệu và xử lý logic dữ liệu.
- **View**: Điều phối dữ liệu giữa Model và Template, xử lý các route và trả về kết quả.
- **Template**: Chứa các file HTML, sử dụng Jinja2 để nhúng dữ liệu động.

## Cơ sở dữ liệu

Hệ thống sử dụng cơ sở dữ liệu quan hệ với các bảng chính sau:

- **Admin**
- **Regulation**
- **User**
- **Profile**
- **Teacher**
- **Staff**
- **Year**
- **Semester**
- **Subject**
- **Class**
- **Student**
- **Score**
- **Teaching_Assignment**
- **Student_Class**
- **Staff_Class**

## Công nghệ sử dụng

- **Python**
- **Flask**
- **SQLAlchemy**
- **Jinja2**
- **ChartJS**

## Cài đặt và chạy dự án


1. **Sao chép mã nguồn dự án từ kho lưu trữ GitHub**

   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```
2. **Cài đặt môi trường ảo Python**

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. **Cài đặt các thư viện cần thiết**

   ```bash
    pip install -r requirements.txt
    ```

4. **Cấu hình cơ sở dữ liệu**

   - Cập nhật thông tin kết nối cơ sở dữ liệu trong file `config.py`.

5. **Chạy ứng dụng Flask**

   ```bash
   flask run
   ```

6. **Truy cập ứng dụng**

   - Mở trình duyệt và truy cập: `http://127.0.0.1:5000`

## Đóng góp

Mọi đóng góp cho dự án đều được chào đón. Vui lòng tạo **Pull Request** hoặc báo cáo lỗi bằng cách tạo **Issue** trên kho lưu trữ GitHub.

## Liên hệ

Vui lòng liên hệ với nhóm phát triển để biết thêm thông tin:

- **Email**: [thien070904@example.com](mailto:thien070904@gmail.com)
- **GitHub**: [Repository](https://github.com/thien070904/StudentManagement)
