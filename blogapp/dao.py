import hashlib
from datetime import date

from blogapp import db

from cloudinary.templatetags import cloudinary

from blogapp.models import User, Post


def get_user_by_id(id):
    return User.query.get(id)

def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username == username.strip(), User.password == password).first()

def load_posts(category_id=None, kw=None):
    query = Post.query
    if category_id:
        query = query.filter(Post.category_id == category_id)
    if kw:
        query = query.filter(Post.title.contains(kw))
    return query.all()


def add_post(title, content, user_id, image=None):
    try:
        today = date.today()

        post_count_today = Post.query.filter(
            Post.user_id == user_id,
            db.func.date(Post.created_date) == today
        ).count()

        if post_count_today >= 10:
            return False, "Bạn đã đạt giới hạn 10 bài đăng trong ngày"

        # Khong duoc dang 2 bai trung tieu de trong 1 ngay
        duplicate_title = Post.query.filter(
            Post.title == title.strip(),
            db.func.date(Post.created_date) == today
        ).first()

        if duplicate_title:
            return False, "Bạn đã đăng bài với tiêu đề này trong hôm nay"

        post = Post(
            title=title.strip(),
            content=content.strip(),
            user_id=user_id
        )

        if image:
            res = cloudinary.uploader.upload(image)
            post.image = res.get('secure_url')

        db.session.add(post)
        db.session.commit()
        return True, "Đăng bài viết thành công"
    except Exception as e:
        db.session.rollback()
        return False, str(e)