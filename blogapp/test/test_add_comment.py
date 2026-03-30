from .base import test_app, test_session
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
    test_session.add(c1)
    test_session.commit()
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

    test_session.add_all([p1, p2, c2, c3, c4, c5, c6, c7, u1, u2])
    test_session.commit()
    return [p1, p2, c1, c2, c3, c4, c5, c6, c7, u1, u2]


def test_locked_comment_post(sample_data):
    ok, msg = dao.check_post_locked(sample_data[0].id)
    assert ok == True
    assert msg is None
    ok, msg = dao.check_post_locked(sample_data[1].id)
    assert ok == False
    assert "Bài viết này đã bị khóa bình luận" in msg
    ok, msg = dao.check_post_locked(3)
    assert ok == False
    assert "Bài viết không tồn tại" in msg


def test_limit_comment(sample_data):
    ok, msg = dao.check_limit_comment(sample_data[9].id, sample_data[0].id)
    assert ok == False
    assert "Bạn đã đạt đến giới hạn bình luận cho bài viết này" in msg
    ok, msg = dao.check_limit_comment(sample_data[10].id, sample_data[0].id)
    assert ok == True
    assert msg is None

def test_anti_spam(sample_data, test_session):
    c = Comment(content="Comment post open 1", user_id=2, post_id=1, parent_id=None,
                 created_date=datetime.now())
    test_session.add(c)
    test_session.commit()
    ok, msg = dao.check_anti_spam(sample_data[10].id)
    assert ok == False
    assert "Vui lòng đợi sau" in msg

    c.created_date = datetime.now() - timedelta(seconds=20)
    test_session.commit()
    ok, msg = dao.check_anti_spam(sample_data[10].id)
    assert ok == True
    assert msg is None


def test_allow_to_comment(sample_data, test_session):
    ok, msg = dao.is_allow_to_comment(sample_data[10].id, sample_data[0].id)
    assert ok == True
    assert msg is None

    ok, msg = dao.is_allow_to_comment(sample_data[10].id, sample_data[1].id)
    assert ok == False
    assert "Bài viết này đã bị khóa bình luận" in msg

    ok, msg = dao.is_allow_to_comment(sample_data[9].id, sample_data[0].id)
    assert ok == False
    assert "Bạn đã đạt đến giới hạn bình luận cho bài viết này" in msg

    new_comment = Comment(
        content="Spam test",
        user_id=sample_data[10].id,
        post_id=sample_data[0].id,
        created_date=datetime.now()
    )
    test_session.add(new_comment)
    test_session.commit()

    ok, msg = dao.is_allow_to_comment(sample_data[10].id, sample_data[0].id)
    assert ok == False
    assert "Vui lòng đợi sau" in msg