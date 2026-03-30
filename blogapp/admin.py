from flask import redirect
from flask_admin import BaseView, expose, AdminIndexView, Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user

from blogapp import app, db
from blogapp.models import UserRole, Post


class AdminView(ModelView):
    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self) -> bool:
        return current_user.is_authenticated

class PostView(AdminView):
    column_list = ['id','title', 'content','is_locked', 'is_pinned', 'user_id']
    column_searchable_list = ['title']
    column_filters = ['id', 'is_locked', 'is_pinned']
    can_export = True
    edit_modal = True
    column_editable_list = ['title']
    page_size = 5


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')

admin = Admin(app=app, name="Blog App Admin", index_view=MyAdminIndexView())

admin.add_view(LogoutView(name='Đăng xuất'))
admin.add_view(PostView(Post, db.session))