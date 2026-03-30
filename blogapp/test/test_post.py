from .base import test_app, test_session
import pytest

from .. import dao
from ..models import Post, Comment

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

def test_existing_post(sample_post):
    actual_post = dao.get_posts()
    assert 1 in [p.id for p in actual_post]

def test_not_existing_post(sample_post):
    u = MockUser(1)
    with pytest.raises(ValueError):
        dao.delete_post(post_id=999, current_user=u)


