from .base import test_app, test_session
import pytest

from .. import dao
from ..models import Post, Comment
from contextlib import nullcontext as does_not_raise


class MockUser:
    def __init__(self, user_id, role='user'):
        self.id = user_id
        self.user_role = role


@pytest.fixture
def sample_post(test_session):
    p1 = Post(id=1, title='bach tuyet va 7 chu lun', content='post content 1', user_id=1, is_locked=False, is_pinned=False)
    p2 = Post(id=2, title='con meo trang va 10 con cho den', content='post content 2', user_id=1, is_locked=False, is_pinned=False)
    p3 = Post(id=3, title='chuyen tinh cua 2 con meo', content='post content 3', user_id=1, is_locked=False, is_pinned=False)
    p4 = Post(id=4, title='dien thoai gia re ???', content='post content 4', user_id=1, is_locked=False, is_pinned=False)
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


def test_existing_post(sample_post):
    actual_post = dao.get_posts()
    assert 1 in [p.id for p in actual_post]


def test_not_existing_post(sample_post):
    u = MockUser(1)
    with pytest.raises(ValueError):
        dao.delete_post(post_id=999, current_user=u)


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

    assert dao.get_posts(id=p.id) is None


def test_delete_wrong_permission(sample_post):
    p = sample_post[0]
    u = MockUser(2)
    with pytest.raises(PermissionError, match='Chỉ admin hoặc tác giả mới được xóa'):
        dao.delete_post(post_id=p.id, current_user=u)


@pytest.mark.parametrize(
    "post_idx, user_id_mock, is_pinned, is_confirmed, expected_exception",
    [
        (0, 1, True, False, pytest.raises(ValueError)),  # bài ghim
        (1, 2, False, False, pytest.raises(PermissionError)),
        (2, 1, False, False, does_not_raise()),  # bài viết có 10 comments
        (3, 1, False, False, does_not_raise()),  # bài viết có 9 comments
        (1, 1, False, False, does_not_raise()),  # bài viết có 0 comments
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


def test_count_posts(sample_post):
    actual_post = dao.get_posts()
    assert len(actual_post) == dao.count_posts()


