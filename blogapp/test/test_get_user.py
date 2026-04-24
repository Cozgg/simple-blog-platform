from .base import test_app, test_session
import pytest

from .. import dao
from ..models import User, UserRole


@pytest.fixture
def sample_user(test_session):
    u1 = User(name='Quản trị viên', username='admin', password="123", avatar="None", email="None", user_role = UserRole.ADMIN)
    u2 = User(name='canh', username='canh', password="123", avatar="None", email="None", user_role = UserRole.USER)
    test_session.add_all([u1, u2])
    test_session.commit()
    return [u1, u2]

def test_get_user_detail(sample_user):
    u = dao.get_user_by_id(1)

    assert u.id == 1
    assert u.name == 'Quản trị viên'
    assert u.user_role == UserRole.ADMIN

def test_get_all_users(sample_user):
    actual_users = dao.get_users()
    assert len(actual_users) == 2
