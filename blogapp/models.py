import enum
import hashlib
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import Column, String, Enum, DateTime, Integer, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from blogapp import db, app


class UserRole(enum.Enum):
    ADMIN = 1
    USER = 2


class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=datetime.now)


class User(BaseModel, UserMixin):
    name = Column(String(100), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    avatar = Column(String(150))
    user_role = Column(Enum(UserRole), default=UserRole.USER)
    email = Column(String(100), nullable=False)

    posts = relationship('Post', backref='author', lazy=True)
    comments = relationship('Comment', backref='user', lazy=True)


class Post(BaseModel):
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    image = Column(String(255))
    is_locked = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey(User.id), nullable=False)

    comments = relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")


class Comment(BaseModel):
    content = Column(String(500), nullable=False)

    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    post_id = Column(Integer, ForeignKey(Post.id), nullable=False)

    parent_id = Column(Integer, ForeignKey('comment.id'))
    replies = relationship('Comment', backref=db.backref('parent', remote_side='Comment.id'), lazy=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        default_avt = "https://res.cloudinary.com/dpl8syyb9/image/upload/v1764237405/ecjxy41wdhl7k03scea8.jpg"


        def hash_pass(password):
            return str(hashlib.md5(password.encode('utf-8')).hexdigest())

        admin_user = User(
            name='Quản trị viên',
            username='admin',
            password=hash_pass("admin123"),
            user_role=UserRole.ADMIN,
            email="admin@blog.com",
            avatar=default_avt
        )

        users = [
            User(name='Huu Cong', username='cozg',
                 password=hash_pass("123456"), user_role=UserRole.USER,
                 email="cozg@gmail.com", avatar=default_avt),
            User(name='Thế Cảnh', username='canhhuynh',
                 password=hash_pass("123456"), user_role=UserRole.USER,
                 email="canh@gmail.com", avatar=default_avt),
            User(name='Nem chua', username='nemchua',
                 password=hash_pass("123456"), user_role=UserRole.USER,
                 email="36@gmail.com", avatar=default_avt)
        ]

        db.session.add(admin_user)
        db.session.add_all(users)
        db.session.commit()

        posts = [
            Post(
                title="Hướng dẫn học Python Flask cho người mới",
                content="Đây là nội dung bài viết hướng dẫn về Flask. Flask là một micro-framework cực kỳ mạnh mẽ và linh hoạt dành cho các nhà phát triển web muốn bắt đầu nhanh chóng.",
                user_id=users[0].id,
                is_pinned=True
            ),
            Post(
                title="Các kỹ thuật kiểm thử phần mềm phổ biến 2026",
                content="Trong môn học Kiểm thử phần mềm, chúng ta cần nắm vững các kỹ thuật như Kiểm thử giá trị biên, Phân vùng tương đương và Kiểm thử tích hợp để đảm bảo chất lượng sản phẩm.",
                user_id=users[1].id
            ),
            Post(
                title="Lộ trình trở thành Fullstack Developer",
                content="Để trở thành Fullstack Developer, bạn cần học tốt cả Frontend (React/Vue) và Backend (Flask/Node.js), kèm theo kiến thức về database như SQL Server hoặc MongoDB.",
                user_id=users[2].id
            )
        ]

        db.session.add_all(posts)

        sample_comment = Comment(
            content="Bài viết rất hay và bổ ích, cảm ơn tác giả!",
            user_id=users[1].id,
            post_id=1
        )
        db.session.add(sample_comment)

        db.session.commit()
        print("Đã import dữ liệu mẫu thành công!")
