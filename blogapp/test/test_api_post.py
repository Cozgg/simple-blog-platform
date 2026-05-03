import pytest
from blogapp.test.base import test_app, test_client, test_session
from blogapp.models import Post, User, UserRole
from blogapp.index import register_routers
import json

def mock_login(mocker, user_id=1, role=UserRole.USER):
    class FakeUser:
        is_authenticated = True
        id = user_id
        user_role = role

    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())
    return FakeUser()

# @pytest.fixture(autouse=True)
# def setup_routes(test_app):
#     register_routers(test_app)

def test_create_post_success(test_client, mocker):
    mock_login(mocker)
    add_post_mock = mocker.patch("blogapp.dao.add_post", return_value=(True, "Đăng bài viết thành công"))

    res = test_client.post(
        "/api/posts",
        data={
            "title": "Tiêu đề bài viết hợp lệ dài trên 10 ký tự",
            "content": "Nội dung bài viết này rất dài và đầy đủ thông tin, chắc chắn trên 50 ký tự để thỏa mãn điều kiện validation của API."
        }
    )

    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == 200
    assert data["msg"] == "Đăng bài viết thành công"
    add_post_mock.assert_called_once()

def test_create_post_invalid_title(test_client, mocker):
    mock_login(mocker)
    
    res = test_client.post(
        "/api/posts",
        data={
            "title": "Ngắn",
            "content": "Nội dung bài viết này rất dài và đầy đủ thông tin, chắc chắn trên 50 ký tự."
        }
    )

    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == 400
    assert "Tiêu đề phải từ 10 đến 200 ký tự" in data["err_msg"]

def test_create_post_invalid_content(test_client, mocker):
    mock_login(mocker)
    
    res = test_client.post(
        "/api/posts",
        data={
            "title": "Tiêu đề bài viết hợp lệ dài trên 10 ký tự",
            "content": "Nội dung ngắn"
        }
    )

    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == 400
    assert "Nội dung phải từ 50 đến 5000 ký tự" in data["err_msg"]


def test_create_post_not_logged_in(test_client, mocker):
    class AnonymousUser:
        is_authenticated = False
    mocker.patch("flask_login.utils._get_user", return_value=AnonymousUser())

    res = test_client.post(
        "/api/posts",
        data={"title": "Test Title", "content": "Test Content"}
    )

    assert res.status_code == 302
