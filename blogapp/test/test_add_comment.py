from .base import test_app, test_session, test_client
import pytest

from .. import dao
from ..models import Post, Comment, User, UserRole
from datetime import datetime, timedelta
import hashlib


@pytest.fixture
def sample_data(test_session):
    u1 = User(name='Ngọc Sơn', username='ngocson',
              password=str(hashlib.md5("123456".encode('utf-8')).hexdigest())
              , user_role=UserRole.USER,
              email="ngocson@gmail.com",
              avatar="https://res.cloudinary.com/dpl8syyb9/image/upload/v1764237405/ecjxy41wdhl7k03scea8.jpg")

    u2 = User(name='Thế Cảnh', username='canhhuynh',
              password=str(hashlib.md5("123456".encode('utf-8')).hexdigest())
              , user_role=UserRole.USER,
              email="ngocson@gmail.com",
              avatar="https://res.cloudinary.com/dpl8syyb9/image/upload/v1764237405/ecjxy41wdhl7k03scea8.jpg")

    p1 = Post(title='Post Open', content='Content 1', user_id=1, is_locked=False)
    p2 = Post(title='Post Locked', content='Content 2', user_id=1, is_locked=True)

    c1 = Comment(content="Comment post open 1", user_id=1, post_id=1, parent_id=None,
                 created_date=datetime.strptime("2026-03-28 20:00:05", "%Y-%m-%d %H:%M:%S"))
    c2 = Comment(content="Comment post open 1", user_id=1, post_id=1, parent_id=c1.id,
                 created_date=datetime.strptime("2026-03-28 22:00:05", "%Y-%m-%d %H:%M:%S"))
    c3 = Comment(content="Comment post open 1", user_id=1, post_id=1, parent_id=c1.id,
                 created_date=datetime.strptime("2026-03-28 22:15:20", "%Y-%m-%d %H:%M:%S"))
    c4 = Comment(content="Comment post open 1", user_id=1, post_id=1, parent_id=None,
                 created_date=datetime.strptime("2026-03-28 22:30:00", "%Y-%m-%d %H:%M:%S"))
    c5 = Comment(content="Comment post open 1", user_id=1, post_id=1, parent_id=None,
                 created_date=datetime.strptime("2026-03-28 22:45:30", "%Y-%m-%d %H:%M:%S"))

    c6 = Comment(content="Comment post open 1", user_id=2, post_id=1, parent_id=None,
                 created_date=datetime.strptime("2026-03-28 22:59:59", "%Y-%m-%d %H:%M:%S"))
    c7 = Comment(content="Comment post open 1", user_id=2, post_id=1, parent_id=None,
                 created_date=datetime.strptime("2026-03-28 23:59:59", "%Y-%m-%d %H:%M:%S"))

    test_session.add_all([p1, p2, c1, c2, c3, c4, c5, c6, c7, u1, u2])
    test_session.commit()
    return [p1, p2, c1, c2, c3, c4, c5, c6, c7, u1, u2]

def test_save_comment_success(sample_data, test_session):
    user_id = sample_data[10].id
    post_id = sample_data[0].id
    content = "Đây là bình luận hợp lệ"

    dao.save_comment(content, post_id, user_id)
    saved_comment = Comment.query.filter_by(content=content, user_id=user_id).first()
    assert saved_comment is not None
    assert saved_comment.post_id == post_id


def test_save_comment_fail_permission(sample_data):
    user_id = sample_data[9].id
    post_id = sample_data[0].id
    content = "Đây là bình luận bị chặn của user 1(đã tới giới hạn)"

    with pytest.raises(PermissionError, match="Bạn đã đạt đến giới hạn bình luận cho bài viết này"):
        assert dao.save_comment(content=content, user_id=user_id, post_id=post_id)


def test_save_comment_fail_locked_or_null_post(sample_data):
    user_id = sample_data[10].id
    post_id = sample_data[1].id
    content = "Bình luận vào post bị khóa(bị chặn)"

    with pytest.raises(PermissionError, match="Bài viết này đã bị khóa bình luận"):
        assert dao.save_comment(content=content, user_id=user_id, post_id=post_id)

    post_id = 3
    content = "Bình luận vào post không tồn tại"

    with pytest.raises(PermissionError, match="Bài viết không tồn tại"):
        assert dao.save_comment(content=content, user_id=user_id, post_id=post_id)

def test_save_comment_fail_anti_spam(sample_data, test_session):
    user_id = sample_data[10].id
    post_id = sample_data[0].id
    content = "Binh luan bi chan do spam"
    recent_comment = Comment(content=content, user_id=user_id, post_id=post_id,
                             created_date=datetime.now())
    test_session.add(recent_comment)
    test_session.commit()

    with pytest.raises(PermissionError, match="Vui lòng đợi sau"):
        assert dao.save_comment(content=content, user_id=user_id, post_id=post_id)

def test_save_comment_pass_after_wait(sample_data, test_session):
    user_id = sample_data[10].id
    post_id = sample_data[0].id
    content = "Binh luan pass sau khi doi 10s 10s"
    old_time = datetime.now() - timedelta(seconds=15)
    old_comment = Comment(content=content, user_id=user_id, post_id=post_id, created_date=old_time)
    test_session.add(old_comment)
    test_session.commit()
    dao.save_comment(content=content, user_id=user_id, post_id=post_id)
    saved_comment = Comment.query.filter_by(content=content).first()
    assert saved_comment is not None
