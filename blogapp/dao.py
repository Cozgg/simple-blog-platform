from datetime import datetime
import hashlib
import re

import cloudinary
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from blogapp import db, app
from blogapp.models import Post, User, UserRole, Comment
from datetime import date


def get_users(id=None):
    query = User.query
    if id:
        return query.get(id)
    return query.all()


def get_posts(kw=None, id=None, page=None):
    query = Post.query
    if id:
        return query.get(id)
    if kw:
        query = query.filter(Post.title.contains(kw))
    if page:
        start = (page - 1) * app.config['PAGE_SIZE']
        query = query.slice(start, start + app.config['PAGE_SIZE'])
    return query.all()


def count_posts():
    return Post.query.count()


def delete_post(post_id, current_user, is_confirmed=False):
    p = Post.query.get(post_id)
    if not p:
        raise ValueError('Bài viết ko tồn tại')

    if p.is_pinned:
        raise ValueError('Bài viết đang ghim không được xóa')

    if p.user_id != current_user.id and current_user.user_role != UserRole.ADMIN:
        raise PermissionError('Chỉ admin hoặc tác giả mới được xóa')

    if len(p.comments) > 10 and not is_confirmed:
        raise ValueError('Bài viết có hơn 10 bình luận, cần xác nhận xóa')

    db.session.delete(p)
    db.session.commit()


def add_user(name, username, password, avatar):
    if len(username) < 5:
        raise ValueError("username phai it nhat co 5 ki tu")
    if len(password) < 8:
        raise ValueError("mat khau phai it nhat co 8 ki tu")
    if not re.search(r'[0-9]', password):
        raise ValueError("Mật khẩu phải chứa ít nhất một chữ số")
    if not re.search(r'[a-z]', password):
        raise ValueError("Mật khẩu phải chứa ít nhất một chữ thường")
    if not re.search(r'[A-Z]', password):
        raise ValueError("Mật khẩu phải chứa ít nhất một chữ hoa")
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(name=name.strip(), username=username.strip(), password=password)
    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res.get("secure_url")

    db.session.add(u)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Exception('Username đã tồn tại!')


def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username == username,
                             User.password == password).first()


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
            Post.user_id == user_id,
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

def check_post_locked(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        return False, 'Bài viết không tồn tại'
    if post.is_locked:
        return False, 'Bài viết này đã bị khóa bình luận'
    return True, None

def check_limit_comment(user_id, post_id):
    count_comment = Comment.query.filter_by(user_id=user_id, post_id=post_id).count()
    if count_comment >= 5:
        return False, "Bạn đã đạt đến giới hạn bình luận cho bài viết này"
    return True, None

def check_anti_spam(user_id):
    last_comment = Comment.query.filter_by(user_id=user_id).order_by(desc(Comment.created_date)).first()
    if last_comment:
        gap = datetime.now() - last_comment.created_date
        if gap.total_seconds() < 10:
            wait = 10 - int(gap.total_seconds())
            return False, f"Vui lòng đợi sau {wait} giây để tiếp tục bình luận"
    return True, None

def is_allow_to_comment(user_id, post_id):
    is_comment_ok, msg_comment = check_limit_comment(user_id,post_id)
    if not is_comment_ok:
        return False, msg_comment

    is_post_open, msg_post = check_post_locked(post_id)
    if not is_post_open:
        return False, msg_post

    is_anti_spam_ok, msg_anti_spam = check_anti_spam(user_id)
    if not is_anti_spam_ok:
        return False, msg_anti_spam

    return True, None

def save_comment(content, post_id, user_id):
    allow, message = is_allow_to_comment(user_id, post_id)
    if not allow:
        raise PermissionError(message)
    try:
        new_comment = Comment(content=content, post_id=post_id,user_id=user_id)
        db.session.add(new_comment)
        db.session.commit()
    except Exception as ex:
        db.session.rollback()