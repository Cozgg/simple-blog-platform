from blogapp import admin, db
from blogapp.models import Post, User, UserRole
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

class BlogAdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

admin.add_view(BlogAdminView(Post, db.session, name='Bài viết'))