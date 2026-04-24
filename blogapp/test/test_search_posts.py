import hashlib

from .base import test_app, test_session
import pytest

from .. import dao
from ..models import Post, User, UserRole


@pytest.fixture
def sample_post(test_session):
    u1 = User(name='Ngọc Sơn', username='ngocson22',
              password=str(hashlib.md5("123456".encode('utf-8')).hexdigest())
              , user_role=UserRole.USER,
              email="ngocson@gmail.com",
              avatar="https://res.cloudinary.com/dpl8syyb9/image/upload/v1764237405/ecjxy41wdhl7k03scea8.jpg")

    u2 = User(name='Thế Cảnh', username='canhhuynh22',
              password=str(hashlib.md5("123456".encode('utf-8')).hexdigest())
              , user_role=UserRole.USER,
              email="ngocson@gmail.com",
              avatar="https://res.cloudinary.com/dpl8syyb9/image/upload/v1764237405/ecjxy41wdhl7k03scea8.jpg")
    p1 = Post(id=1, title='bach tuyet va 7 chu lun', content='post content 1', user_id=1, is_locked=False, is_pinned=False)
    p2 = Post(id=2, title='con meo trang va 10 con cho den', content='post content 2', user_id=1, is_locked=False, is_pinned=False)
    p3 = Post(id=3, title='chuyen tinh cua 2 con meo', content='post content 3', user_id=1, is_locked=False, is_pinned=False)
    p4 = Post(id=4, title='dien thoai gia re ???', content='post content 4', user_id=1, is_locked=False, is_pinned=False)

    test_session.add_all([p1, p2, p3, p4, u1, u2])
    test_session.commit()
    return [p1, p2, p3, p4, u1, u2]

def test_keyword(sample_post):
    actual_posts = dao.get_posts(kw="meo")
    assert len(actual_posts) == 2
    assert all("meo" in p.title for p in actual_posts)

def test_pagination(sample_post):
    actual_posts = dao.get_posts(page=1)
    assert len(actual_posts) == 4