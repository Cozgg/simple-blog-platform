import pytest
from flask_login import current_user

from blogapp.models import UserRole
from blogapp.test.base import test_client, test_app, test_session
def mock_login(mocker, user_id=1, role=UserRole.USER):
    class FakeUser:
        is_authenticated = True
        id = user_id
        user_role = role

    user = FakeUser()

    mocker.patch("flask_login.utils._get_user", return_value=user)
    return user

def test_delete_post_success_no_comment(test_client, mocker):
    mock_login(mocker=mocker)
    delete_post_mock = mocker.patch("blogapp.dao.delete_post")

    res = test_client.delete(
        "/api/posts/1"
    )

    data = res.get_json()

    assert data["status"] == 204
    assert data["msg"] == "Xóa thành công"
    delete_post_mock.assert_called_once()


def test_delete_post_success_with_confirmed(test_client, mocker):
    mock_login(mocker=mocker)
    delete_post_mock = mocker.patch("blogapp.dao.delete_post")

    res = test_client.delete("/api/posts/1?confirmed=true")

    data = res.get_json()
    assert data["status"] == 204
    assert data["msg"] == "Xóa thành công"
    delete_post_mock.assert_called_once_with(post_id=1, current_user=mocker.ANY, is_confirmed='true')

@pytest.mark.parametrize("exception_mock, err_msg", [
    (ValueError('Bài viết ko tồn tại'), 'Bài viết ko tồn tại'),
    (ValueError('Bài viết đang ghim không được xóa'), 'Bài viết đang ghim không được xóa'),
    (PermissionError('Chỉ admin hoặc tác giả mới được xóa'), 'Chỉ admin hoặc tác giả mới được xóa'),
    (ValueError('Bài viết có hơn 10 bình luận, cần xác nhận xóa'), 'Bài viết có hơn 10 bình luận, cần xác nhận xóa')
])
def test_delete_post_error(test_client, mocker, exception_mock, err_msg):
    mock_login(mocker)
    mocker.patch("blogapp.dao.delete_post", side_effect=exception_mock)

    res = test_client.delete("/api/posts/1")

    data = res.get_json()
    assert data["status"] == 400
    assert data["err_msg"] == err_msg


