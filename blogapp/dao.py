import hashlib
import re

import cloudinary
from sqlalchemy.exc import IntegrityError

from blogapp import db
from blogapp.models import Post, User, UserRole


def get_users(id = None):
    query = User.query
    if id:
        return query.get(id)
    return query.all()

def get_posts(id = None):
    query = Post.query
    if id:
        return query.get(id)
    return query.all()

def delete_post(post_id, current_user, is_confirmed=False):
    p = Post.query.get(post_id)
    if not p:
        raise ValueError('Bài viết ko tồn tại')

    if p.user_id != current_user.id and current_user.user_role != UserRole.ADMIN:
        raise PermissionError('Chỉ admin hoặc tác giả mới được xóa')

    if p.is_pinned:
        raise ValueError('Bài viết đang ghim không được xóa')

    if len(p.comments) > 10 and not is_confirmed:
        raise ValueError('Bài viết có hơn 10 bình luận, cần xác nhận xóa')

    db.session.delete(p)
    db.session.commit()

def add_user(name, username, password, avatar):
    if len(username) < 5:
        raise ValueError("username phai it nhat co 5 ki tu")
    if len(password) <8:
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
    return User.query.filter(User.username==username,
                             User.password==password).first()

def get_user_by_id(id):
    return User.query.get(id)
