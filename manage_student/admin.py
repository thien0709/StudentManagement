from flask import redirect, request
from flask_admin import Admin, expose, AdminIndexView
from flask_admin import BaseView
from flask_admin.contrib.sqla import ModelView
from manage_student.models import *
from manage_student import app
from flask_login import logout_user, current_user


class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/login')

    def is_accessible(self):
        return current_user.is_authenticated

class RegulationsView(AuthenticatedView):
    column_labels = {
        'type': 'Loại quy định',
        'regulation_name': 'Tên quy định',
        'min': 'Giá trị tối thiểu',
        'max': 'Giá trị tối đa',
    }

class TeacherSubjectView(AuthenticatedView):
    column_list = ('teacher_id', 'subject_id', 'grade')
    column_filters = ['teacher_id', 'subject_id']
    column_labels = {
        'teacher_id': 'Giáo viên',
        'subject_id': 'Môn học',
        'grade': 'Khối'
    }
    def _teacher_name(view, context, model, name):
        return "ID giáo viên: {} | {}".format(model.teacher_id, model.teacher.user.profile.name)

    def _subject_name(view, context, model, name):
        return "ID môn học : {} | {}".format(model.subject_id, model.subject.name)

    def _grade_name(view, context, model, name):
        return model.subject.grade.value

    column_formatters = {
        'teacher_id': _teacher_name,
        'subject_id': _subject_name,
        'grade': _grade_name,
    }


admin = Admin(app, name='Quản lý học sinh', template_mode='bootstrap4')
admin.add_view(AuthenticatedView(Subject, db.session, name="Danh sách môn học"))
admin.add_view(TeacherSubjectView(Teachers_Subject, db.session, name="Phân công giáo viên"))
admin.add_view(RegulationsView(Regulation, db.session, name="Chỉnh sửa quy định"))
admin.add_view(LogoutView(name='Đăng xuất'))