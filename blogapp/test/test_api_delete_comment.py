import pytest
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

def test_delete_comment_api_success(test_client, mocker):
    mock_login(mocker)

    success_msg = "Đã xóa bình luận và 2 phản hồi liên quan."
    delete_mock = mocker.patch("blogapp.dao.delete_comment", return_value=(True, success_msg))

    res = test_client.delete("/api/comments/10")

    data = res.get_json()
    assert data["status"] == 204
    assert data["msg"] == success_msg

    delete_mock.assert_called_once()

@pytest.mark.parametrize("dao_exception, expected_status, expected_err_msg", [
    (ValueError("Bình luận không tồn tại."), 404, "Bình luận không tồn tại."),
    (PermissionError("Bạn không có quyền xóa."), 403, "Bạn không có quyền xóa."),
    (Exception("Database error"), 500, "Lỗi hệ thống không xác định")
])
def test_delete_comment_api_errors(test_client, mocker, dao_exception, expected_status, expected_err_msg):
    mock_login(mocker)

    mocker.patch("blogapp.dao.delete_comment", side_effect=dao_exception)

    res = test_client.delete("/api/comments/10")
    data = res.get_json()

    assert data["status"] == expected_status
    assert expected_err_msg in data["err_msg"]