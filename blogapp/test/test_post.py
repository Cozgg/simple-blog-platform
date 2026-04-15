import pytest
from unittest.mock import patch
from .base import test_app, test_session, test_client
from .. import dao
from ..models import Post, Comment, User, UserRole
from cloudinary import uploader
import cloudinary.uploader

from contextlib import nullcontext as does_not_raise



class MockUser:
    def __init__(self, user_id, role='user'):
        self.id = user_id
        self.user_role = role

@pytest.fixture
def sample_post(test_session):
    p1 = Post(id=1, title='post 1', content='post content 1', user_id=1, is_locked=False, is_pinned=False)
    p2 = Post(id=2, title='post 2', content='post content 2', user_id=1, is_locked=False, is_pinned=False)
    p3 = Post(id=3, title='post 3', content='post content 3', user_id=1, is_locked=False, is_pinned=False)
    p4 = Post(id=4, title='post 4', content='post content 4', user_id=1, is_locked=False, is_pinned=False)
    comments = []
    for i in range(1, 12):
        c = Comment(content=f"comment {i}", user_id=1 if i % 2 == 0 else 2, post_id=p1.id, parent_id=None)
        if i > 1:
            c1 = Comment(content=f"comment {i}", user_id=1 if i % 2 == 0 else 2, post_id=p3.id, parent_id=None)
            comments.append(c1)
        if i > 2:
            c2 = Comment(content=f"comment {i}", user_id=1 if i % 2 == 0 else 2, post_id=p4.id, parent_id=None)
            comments.append(c2)
        comments.append(c)
    test_session.add_all([p1, p2, p3, p4] + comments)
    test_session.commit()
    return [p1, p2, p3, p4] + comments


@pytest.fixture
def setup_user(test_session):
    import hashlib
    pw_hash = str(hashlib.md5("123456".encode('utf-8')).hexdigest())
    u = User(name="Test User", username="testuser", password=pw_hash, email="test@gmail.com", user_role=UserRole.USER)
    test_session.add(u)
    test_session.commit()
    return u

def test_existing_post(sample_post):
    actual_post = dao.get_posts()
    assert 1 in [p.id for p in actual_post]


def test_not_existing_post(sample_post):
    u = MockUser(1)
    with pytest.raises(ValueError):
        dao.delete_post(post_id=999, current_user=u)


def test_post_limit(test_session, setup_user):
    user_id = setup_user.id
    content_valid = "Nội dung này đủ dài để pass qua việc kiểm tra độ dài. OKE LUON E NHE"

    title_duplicate = "Tiêu đề dùng để test trùng lặp"
    success1, _ = dao.add_post(title_duplicate, content_valid, user_id)
    assert success1 is True

    success2, msg2 = dao.add_post(title_duplicate, content_valid, user_id)
    assert success2 is False
    assert "đã đăng bài với tiêu đề này" in msg2

    for i in range(1, 10):
        title = f"Tiêu đề không trùng lặp số {i} hợp lệ"
        success, _ = dao.add_post(title, content_valid, user_id)
        assert success is True

    success_11, msg_11 = dao.add_post("Tiêu đề bài thứ 11", content_valid, user_id)
    assert success_11 is False
    assert "giới hạn 10 bài" in msg_11


@patch('cloudinary.uploader.upload')
def test_add_post_with_image(mock_upload, test_session, setup_user):
    mock_upload.return_value = {'secure_url': 'https://res.cloudinary.com/mock-image-url.jpg'}
    success, msg = dao.add_post("Tiêu đề có hình ảnh đính kèm", "Nội dung bài viết này có kèm theo hình ảnh rất đẹp dài hơn 50 ký tự nha.", setup_user.id, image="dummy_image")
    assert success is True

@patch('blogapp.dao.db.session.commit')
def test_add_post_exception(mock_commit, test_session, setup_user):
    mock_commit.side_effect = Exception("Lỗi Database giả lập")
    success, msg = dao.add_post("Tiêu đề gây lỗi hệ thống", "Nội dung để test hệ thống keke, 12345678900---63142.", setup_user.id)
    assert success is False
    assert "Lỗi Database giả lập" in msg

@pytest.mark.parametrize("title_len, content_len, expected_status", [
    (9, 100, 400),    # Title < 10 (lỗi)
    (10, 100, 200),   # Title = 10 (thành công)
    (200, 100, 200),  # Title = 200 (thành công)
    (201, 100, 400),  # Title > 200 (lỗi)
    (50, 49, 400),    # Content < 50 (lỗi)
    (50, 50, 200),    # Content = 50 (thành công)
    (50, 5000, 200),  # Content = 5000 (thành công)
    (50, 5001, 400),  # Content > 5000 (lỗi)
])
def test_create_post_validation_boundary(test_client, setup_user, title_len, content_len, expected_status):
    test_client.post('/login', data={'username': 'testuser', 'password': '123456'})
    response = test_client.post('/api/posts', data={
        'title': "A" * title_len,
        'content': "B" * content_len
    })
    assert response.get_json()['status'] == expected_status

def test_delete_pinned_post(sample_post):
    p = sample_post[0]
    p.is_pinned = True

    u = MockUser(1)
    with pytest.raises(ValueError, match="Bài viết đang ghim không được xóa"):
        dao.delete_post(post_id=p.id, current_user=u)


def test_delete_over_10_comments(sample_post):
    p = sample_post[0]
    u = MockUser(1)
    with pytest.raises(ValueError, match="Bài viết có hơn 10 bình luận, cần xác nhận xóa"):
        dao.delete_post(post_id=p.id, current_user=u)


def test_delete_over_10_comments_confirmed(sample_post):
    p = sample_post[0]
    u = MockUser(1)
    dao.delete_post(post_id=p.id, current_user=u, is_confirmed=True)

    assert dao.get_posts(p.id) is None


def test_delete_wrong_permission(sample_post):
    p = sample_post[0]
    u = MockUser(2)
    with pytest.raises(PermissionError, match='Chỉ admin hoặc tác giả mới được xóa'):
        assert dao.delete_post(post_id=p.id, current_user=u)


@pytest.mark.parametrize(
    "post_idx, user_id_mock, is_pinned, is_confirmed, expected_exception",
    [
        (0, 1, True, False, pytest.raises(ValueError)),  # bài ghim
        (1, 2, False, False, pytest.raises(PermissionError)),
        (2, 1, False, False, does_not_raise()),  # bài viết có 10 comments
        (3, 1, False, False, does_not_raise()),  # bài viết có 9 comments
        (2, 1, False, False, does_not_raise()),  # bài viết có 0 comments
        (0, 1, False, False, pytest.raises(ValueError)),  # Lỗi > 10 comment nhưng chưa confirm
        (0, 1, False, True, does_not_raise()),  # Xóa thành công (> 10 comment và đã confirm)
    ]
)
def test_delete_post_all(sample_post, post_idx, user_id_mock, is_pinned, is_confirmed, expected_exception):
    p = sample_post[post_idx]
    p.is_pinned = is_pinned
    u = MockUser(user_id=user_id_mock)

    with expected_exception:
        dao.delete_post(post_id=p.id, current_user=u, is_confirmed=is_confirmed)
