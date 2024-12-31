from flask import redirect, flash, url_for
from flask_admin import Admin, expose, BaseView
from flask_admin.contrib.sqla import ModelView
from manage_student.models import UserRole, Subject, Regulation, Class, User
from manage_student import app, db
from flask_login import logout_user, current_user


# Custom ModelView that enforces authentication and admin access
class AuthenticatedView(ModelView):
    def is_accessible(self):
        if not current_user.is_authenticated:
            flash("Vui lòng đăng nhập để truy cập!", "error")
            return False
        if current_user.role != UserRole.ADMIN:
            flash("Bạn không có quyền truy cập vào trang này.", "error")
            return False
        return True


# Logout functionality integrated into Flask-Admin
class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        flash("Đăng xuất thành công.", "success")
        return redirect('/login')

# ModelView for managing regulations with custom column labels
class RegulationsView(AuthenticatedView):
    column_list = ('name', 'min_value', 'max_value')
    column_labels = {
        'name': 'Tên quy định',
        'min_value': 'Giá trị tối thiểu',
        'max_value': 'Giá trị tối đa',
    }
    form_columns = ['name', 'min_value', 'max_value']
    column_filters = ['name']

    can_delete = False
    can_create = False

    form_widget_args = {
        'name': {
            'readonly': True
        }
    }

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.admin_id = current_user.id
        return super(RegulationsView, self).on_model_change(form, model, is_created)


# ModelView for managing subjects
class SubjectView(AuthenticatedView):
    column_list = ('id', 'name', 'score_pass')
    column_labels = {
        'id': 'ID',
        'name': 'Tên Môn Học',
        'score_pass': 'Điểm Qua Môn',
    }
    form_columns = ['name', 'score_pass']
    column_filters = ['name']


# Custom admin view for displaying charts
class CustomAdminView(BaseView):
    @expose('/')
    def index(self):
        # Nội dung HTML sẽ được hiển thị ngay trong trang quản trị Flask-Admin
        return self.render('/admin/chartScreen.html')

    def is_accessible(self):
        if not current_user.is_authenticated:
            flash("Vui lòng đăng nhập để truy cập!", "error")
            return False
        if current_user.role != UserRole.ADMIN:
            flash("Bạn không có quyền truy cập vào trang này.", "error")
            return False
        return True

    def inaccessible_callback(self, name, **kwargs):
        flash("Bạn không có quyền truy cập. Bạn sẽ được chuyển về trang chủ.", "error")
        return redirect(url_for('index'))


class UserView(ModelView):
    column_list = ('id', 'username', 'role', 'profile', 'avatar')
    column_labels = {
        'id': 'ID',
        'username': 'Tên người dùng',
        'role': 'Vai trò',
        'profile': 'Hồ sơ',
        'avatar': 'Ảnh đại diện'
    }
    can_delete = False
    can_create = False
    form_columns = ['username', 'password', 'role', 'avatar', 'profile']
    column_filters = ['username', 'role']

class UserAdd(BaseView):
    @expose('/')
    def index(self):
        # Nội dung HTML sẽ được hiển thị ngay trong trang quản trị Flask-Admin
        return self.render('/admin/register.html')

# Initialize the Flask-Admin interface
admin = Admin(app, name='Quản lý học sinh', template_mode='bootstrap4')

# Add views to the admin interface
admin.add_view(SubjectView(Subject, db.session, name="Danh sách môn học"))
admin.add_view(RegulationsView(Regulation, db.session, name="Chỉnh sửa quy định"))
admin.add_view(CustomAdminView(name='Xem biểu đồ'))
admin.add_view(UserView(User, db.session, name="Danh sách người dùng"))
admin.add_view(UserAdd(name='Thêm người dùng'))
admin.add_view(LogoutView(name='Đăng xuất'))
