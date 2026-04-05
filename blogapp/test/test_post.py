from .base import test_app, test_session
import pytest

from .. import dao
from ..models import Post, Comment, User, UserRole

class MockUser:
    def __init__(self, user_id, role='user'):
        self.id = user_id
        self.role = role

@pytest.fixture
def sample_post(test_session):
    p1 = Post(id=1, title='post 1', content='post content 1', user_id=1, is_locked=False, is_pinned=False)
    p2 = Post(id=2, title='post 2', content='post content 2', user_id=2, is_locked=False, is_pinned=False)
    comments = []
    for i in range(1, 12):
        c = Comment(content=f"comment {i}", user_id=1 if i % 2 == 0 else 2, post_id=p1.id, parent_id=None)
        comments.append(c)
    test_session.add_all([p1, p2] + comments)
    test_session.commit()
    return [p1, p2] + comments

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


@patch('blogapp.dao.cloudinary.uploader.upload')
def test_add_post_with_image(mock_upload, test_session, setup_user):
    mock_upload.return_value = {'secure_url': 'https://res.cloudinary.com/mock-image-url.jpg'}

    user_id = setup_user.id
    title = "Tiêu đề có hình ảnh đính kèm"
    content = "Nội dung bài viết này có kèm theo hình ảnh rất đẹp."
    fake_image = "dummy_image_data"

    success, msg = dao.add_post(title, content, user_id, image=fake_image)

    assert success is True
    assert msg == "Đăng bài viết thành công"

    mock_upload.assert_called_once_with(fake_image)

    saved_post = Post.query.filter_by(title=title).first()
    assert saved_post is not None
    assert saved_post.image == 'https://res.cloudinary.com/mock-image-url.jpg'


@patch('blogapp.dao.db.session.commit')
def test_add_post_exception(mock_commit, test_session, setup_user):
    mock_commit.side_effect = Exception("Lỗi Database giả lập")

    user_id = setup_user.id
    title = "Tiêu đề gây lỗi hệ thống"
    content = "Nội dung không quan trọng vì lỗi sẽ văng ra khi commit."

    success, msg = dao.add_post(title, content, user_id)

    assert success is False
    assert "Lỗi Database giả lập" in msg

