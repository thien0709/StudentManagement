## Hệ Thống Quản Lý Sinh Viên
### Giới thiệu
Hệ thống "Quản Lý Sinh Viên" là một phần mềm được phát triển để hỗ trợ việc quản lý thông tin và hoạt động học tập của học sinh trong nhà trường.
### Chức năng chính
#### Tiếp nhận học sinh mới
#### Lập và quản lý danh sách lớp
#### Nhập và xuất điểm số
#### Thống kê và báo cáo kết quả học tập bằng biểu đồ
#### Phân quyền truy cập theo vai trò (quản trị viên, nhân viên, giáo viên)
#### Tùy chỉnh quy định về độ tuổi tiếp nhận, sĩ số lớp học, cột điểm, môn học
### Kiến trúc hệ thống
##### Hệ thống sử dụng kiến trúc MVT (Model - View - Template):
###### Model: Định nghĩa bảng cơ sở dữ liệu và xử lý logic dữ liệu.
View: Điều phối dữ liệu giữa Model và Template, xử lý các route và trả về kết quả.
Template: Chứa các file HTML, sử dụng Jinja2 để nhúng dữ liệu động.
### Cơ sở dữ liệu
Hệ thống sử dụng cơ sở dữ liệu quan hệ với các bảng sau:
Admin
Regulation
User
Profile
Teacher
Staff
Year
Semester
Subject
Class
Student
Score
Teaching_Assignment
Student_Class
Staff_Class
Công nghệ sử dụng
Python
Flask
SQLAlchemy
Jinja2
ChartJS
Cài đặt và chạy dự án
1.
Cài đặt Python và các thư viện cần thiết.
2.
Sao chép mã nguồn dự án từ kho lưu trữ GitHub.
3.
Cấu hình cơ sở dữ liệu.
4.
Chạy ứng dụng Flask.
Đóng góp
Mọi đóng góp cho dự án đều được chào đón.
Liên hệ
Vui lòng liên hệ với nhóm phát triển để biết thêm thông tin.
This information is from the sources you provided.
