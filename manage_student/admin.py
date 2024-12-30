from flask import redirect, flash, url_for
from flask_admin import Admin, expose, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_login import logout_user, current_user
from manage_student import app, db
from manage_student.models import UserRole, Subject, Regulation


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

    def inaccessible_callback(self, name, **kwargs):
        flash("Bạn không có quyền truy cập. Bạn sẽ được chuyển về trang chủ.", "error")
        return redirect(url_for('index'))


# Logout functionality integrated into Flask-Admin
class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        flash("Đăng xuất thành công.", "success")
        return redirect('/login')

    def is_accessible(self):
        if not current_user.is_authenticated:
            flash("Vui lòng đăng nhập để truy cập!", "error")
            return False
        return True

    def inaccessible_callback(self, name, **kwargs):
        flash("Bạn không có quyền truy cập. Bạn sẽ được chuyển về trang chủ.", "error")
        return redirect(url_for('index'))


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


# Initialize the Flask-Admin interface
admin = Admin(app, name='Quản lý học sinh', template_mode='bootstrap4')

# Add views to the admin interface
admin.add_view(SubjectView(Subject, db.session, name="Danh sách môn học"))
admin.add_view(RegulationsView(Regulation, db.session, name="Chỉnh sửa quy định"))
admin.add_view(CustomAdminView(name='Xem biểu đồ'))
admin.add_view(LogoutView(name='Đăng xuất'))
