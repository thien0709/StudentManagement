from flask import redirect
from flask_admin import Admin, expose, BaseView
from flask_admin.contrib.sqla import ModelView
from manage_student.models import UserRole, Subject, Regulation, Class
from manage_student import app, db
from flask_login import logout_user, current_user


# Custom ModelView that enforces authentication and admin access
class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserRole.ADMIN


# Logout functionality integrated into Flask-Admin
class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/login')

    def is_accessible(self):
        return current_user.is_authenticated


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
    # can_create = True
    # can_edit = True
    # can_delete = True
    # can_view_details = True


class SubjectView(AuthenticatedView):
    column_list = ('id', 'name', 'score_pass')
    column_labels = {
        'id': 'ID',
        'name': 'Tên Môn Học',
        'score_pass': 'Điểm Qua Môn',
    }
    form_columns = ['name', 'score_pass']
    column_filters = ['name']


# Initialize the Flask-Admin interface
admin = Admin(app, name='Quản lý học sinh', template_mode='bootstrap4')

# Add views to the admin interface
admin.add_view(SubjectView(Subject, db.session, name="Danh sách môn học"))
admin.add_view(RegulationsView(Regulation, db.session, name="Chỉnh sửa quy định"))
admin.add_view(LogoutView(name='Đăng xuất'))

# Future View Placeholder (Commented for Now)
# admin.add_view(TeacherTeachingAssignmentView(TeachingAssignment, db.session, name="Phân công giáo viên"))
