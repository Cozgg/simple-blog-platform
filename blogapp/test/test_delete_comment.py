from .base import test_app, test_session, test_client
import pytest

from .. import dao
from ..models import Post, Comment, User, UserRole
from datetime import datetime
import hashlib

@pytest.fixture
def sample_data(test_session):
    u1 = User(name='Ngọc Sơn', username='ngocson',
              password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
              user_role=UserRole.USER,
              email="ngocson@gmail.com",
              avatar="https://res.cloudinary.com/dpl8syyb9/image/upload/v1764237405/ecjxy41wdhl7k03scea8.jpg")

    u2 = User(name='Thế Cảnh', username='canhhuynh',
              password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
              user_role=UserRole.USER,
              email="thecanh@gmail.com",
              avatar="https://res.cloudinary.com/dpl8syyb9/image/upload/v1764237405/ecjxy41wdhl7k03scea8.jpg")

    test_session.add_all([u1, u2])
    test_session.commit()

    p1 = Post(title='Post Open', content='Content 1', user_id=u1.id, is_locked=False)
    p2 = Post(title='Post Locked', content='Content 2', user_id=u1.id, is_locked=True)

    test_session.add_all([p1, p2])
    test_session.commit()

    c1 = Comment(content="Comment post open 1", user_id=u1.id, post_id=p1.id, parent_id=None,
                 created_date=datetime.strptime("2026-03-28 20:00:05", "%Y-%m-%d %H:%M:%S"))
    test_session.add(c1)
    test_session.commit()

    c2 = Comment(content="Comment post open 1", user_id=u1.id, post_id=p1.id, parent_id=c1.id,
                 created_date=datetime.strptime("2026-03-28 22:00:05", "%Y-%m-%d %H:%M:%S"))
    c3 = Comment(content="Comment post open 1", user_id=u1.id, post_id=p1.id, parent_id=c1.id,
                 created_date=datetime.strptime("2026-03-28 22:15:20", "%Y-%m-%d %H:%M:%S"))
    test_session.add(c3)
    test_session.commit()
    c4 = Comment(content="Comment post open 1", user_id=u1.id, post_id=p1.id, parent_id=None,
                 created_date=datetime.strptime("2026-03-28 22:30:00", "%Y-%m-%d %H:%M:%S"))
    c5 = Comment(content="Comment post open 1", user_id=u1.id, post_id=p1.id, parent_id=c3.id,
                 created_date=datetime.strptime("2026-03-28 22:45:30", "%Y-%m-%d %H:%M:%S"))

    c6 = Comment(content="Comment post open 1", user_id=u2.id, post_id=p1.id, parent_id=None,
                 created_date=datetime.strptime("2026-03-28 22:59:59", "%Y-%m-%d %H:%M:%S"))

    c7 = Comment(content="Comment post open 1", user_id=u2.id, post_id=p1.id, parent_id=None,
                 created_date=datetime.strptime("2026-03-28 23:59:59", "%Y-%m-%d %H:%M:%S"))

    test_session.add_all([c2, c4, c5, c6, c7])
    test_session.commit()

    return [p1, p2, c1, c2, c3, c4, c5, c6, c7, u1, u2]

def test_has_child_comments(sample_data, test_session):
    assert dao.has_child_comments(sample_data[2].id) is True
    assert dao.has_child_comments(sample_data[3].id) is False
    assert dao.has_child_comments(sample_data[4].id) is True

def test_get_all_child_ids(test_session, sample_data):
    ids = dao.get_all_child_ids(sample_data[2].id)
    assert set(ids) == {sample_data[3].id, sample_data[4].id, sample_data[6].id}

    ids = dao.get_all_child_ids(sample_data[4].id)
    assert ids == [sample_data[6].id]

    ids = dao.get_all_child_ids(sample_data[3].id)
    assert ids == []

    ids = dao.get_all_child_ids(9999)
    assert ids == []

def test_delete_comment_by_comment_owner(test_session, sample_data):
    c1_id = sample_data[2].id
    c2_id = sample_data[3].id
    c3_id = sample_data[4].id
    c5_id = sample_data[6].id
    u1_id = sample_data[9].id

    ids_to_check = [c1_id, c2_id, c3_id, c5_id]

    success, msg = dao.delete_comment(c1_id, u1_id)
    assert success is True
    deleted = Comment.query.filter(Comment.id.in_(ids_to_check)).all()
    assert deleted == []
    assert "Đã xóa bình luận" in msg

def test_delete_comment_by_post_owner(test_session, sample_data):
    c6_id = sample_data[7].id
    u1_id = sample_data[9].id

    success, msg = dao.delete_comment(c6_id, u1_id)

    assert success is True
    assert "Đã xóa bình luận" in msg
    assert Comment.query.get(c6_id) is None

def test_delete_comment_no_permission(test_session, sample_data):
    with pytest.raises(PermissionError, match='Bạn không có quyền xóa'):
        assert dao.delete_comment(sample_data[2].id, sample_data[10].id)

    assert Comment.query.get(sample_data[2].id) is not None

def test_delete_non_existent_comment(test_session, sample_data):
    count_before = Comment.query.count()
    with pytest.raises(ValueError, match='Bình luận không tồn tại.'):
        assert dao.delete_comment(9999, sample_data[9].id)

    count_after = Comment.query.count()
    assert count_before == count_after