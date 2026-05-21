from pytest_mock import mocker
from blogapp.test.base import test_app, test_client, test_session


def mock_login(mocker):
    class FakeUser:
        is_authenticated = True
        id = 1

    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())


def test_pinned_success(test_client, mocker):
    mocker.patch(
        "blogapp.dao.pinned_post",
        return_value=(True, "Ghim thành công")
    )

    res = test_client.patch('/api/posts/1/pinned')

    data = res.get_json()

    assert data["status"] == 200
    assert data["msg"] == "Ghim thành công"


def test_unpinned_success(test_client, mocker):
    mocker.patch(
        "blogapp.dao.unpinned_post",
        return_value=(True, "Bỏ ghim thành công")
    )

    res = test_client.patch('/api/posts/1/unpinned')

    data = res.get_json()

    assert data["status"] == 200
    assert data["msg"] == "Bỏ ghim thành công"


def test_locked_success(test_client, mocker):
    mocker.patch(
        "blogapp.dao.lock_post",
        return_value=(True, "Khóa thành công")
    )

    res = test_client.patch('/api/posts/1/locked')

    data = res.get_json()

    assert data["status"] == 200
    assert data["msg"] == "Khóa thành công"


def test_unlocked_success(test_client, mocker):
    mocker.patch(
        "blogapp.dao.unlock_post",
        return_value=(True, "Mở khóa thành công")
    )

    res = test_client.patch('/api/posts/1/unlocked')

    data = res.get_json()

    assert data["status"] == 200
    assert data["msg"] == "Mở khóa thành công"


def test_pinned_post_not_found(test_client, mocker):
    mocker.patch(
        "blogapp.dao.pinned_post",
        return_value=(False, "Bài viết không tồn tại")
    )

    res = test_client.patch('/api/posts/999/pinned')

    data = res.get_json()

    assert data["status"] == 400
    assert data["err_msg"] == "Bài viết không tồn tại"


def test_pinned_post_already_pinned(test_client, mocker):
    mocker.patch(
        "blogapp.dao.pinned_post",
        return_value=(False, "Bài viết đã được ghim")
    )

    res = test_client.patch('/api/posts/1/pinned')

    data = res.get_json()

    assert data["status"] == 400
    assert data["err_msg"] == "Bài viết đã được ghim"


def test_pinned_post_not_owner(test_client, mocker):
    mocker.patch(
        "blogapp.dao.pinned_post",
        return_value=(False, "Bài viết không phải của bạn, không thể ghim")
    )

    res = test_client.patch('/api/posts/1/pinned')

    data = res.get_json()

    assert data["status"] == 400
    assert data["err_msg"] == "Bài viết không phải của bạn, không thể ghim"


def test_unpinned_post_not_found(test_client, mocker):
    mocker.patch(
        "blogapp.dao.unpinned_post",
        return_value=(False, "Bài viết không tồn tại")
    )

    res = test_client.patch('/api/posts/999/unpinned')

    data = res.get_json()

    assert data["status"] == 400
    assert data["err_msg"] == "Bài viết không tồn tại"


def test_unpinned_post_not_pinned(test_client, mocker):
    mocker.patch(
        "blogapp.dao.unpinned_post",
        return_value=(False, "Bài viết chưa bị ghim, không thể bỏ ghim")
    )

    res = test_client.patch('/api/posts/1/unpinned')

    data = res.get_json()

    assert data["status"] == 400
    assert data["err_msg"] == "Bài viết chưa bị ghim, không thể bỏ ghim"


def test_unpinned_post_not_owner(test_client, mocker):
    mocker.patch(
        "blogapp.dao.unpinned_post",
        return_value=(False, "Bài viết không phải của bạn, không thể bỏ ghim")
    )

    res = test_client.patch('/api/posts/1/unpinned')

    data = res.get_json()

    assert data["status"] == 400
    assert data["err_msg"] == "Bài viết không phải của bạn, không thể bỏ ghim"


def test_locked_post_not_found(test_client, mocker):
    mocker.patch(
        "blogapp.dao.lock_post",
        return_value=(False, "Bài viết không tồn tại")
    )

    res = test_client.patch('/api/posts/999/locked')

    data = res.get_json()

    assert data["status"] == 400
    assert data["err_msg"] == "Bài viết không tồn tại"


def test_locked_post_already_locked(test_client, mocker):
    mocker.patch(
        "blogapp.dao.lock_post",
        return_value=(False, "Bài viết đã bị khóa")
    )

    res = test_client.patch('/api/posts/1/locked')

    data = res.get_json()

    assert data["status"] == 400
    assert data["err_msg"] == "Bài viết đã bị khóa"


def test_locked_post_not_owner(test_client, mocker):
    mocker.patch(
        "blogapp.dao.lock_post",
        return_value=(False, "Bài viết không phải của bạn, không thể khóa")
    )

    res = test_client.patch('/api/posts/1/locked')

    data = res.get_json()

    assert data["status"] == 400
    assert data["err_msg"] == "Bài viết không phải của bạn, không thể khóa"


def test_unlocked_post_not_found(test_client, mocker):
    mocker.patch(
        "blogapp.dao.unlock_post",
        return_value=(False, "Bài viết không tồn tại")
    )

    res = test_client.patch('/api/posts/999/unlocked')

    data = res.get_json()

    assert data["status"] == 400
    assert data["err_msg"] == "Bài viết không tồn tại"


def test_unlocked_post_not_locked(test_client, mocker):
    mocker.patch(
        "blogapp.dao.unlock_post",
        return_value=(False, "Bài viết không bị khóa, không thể mở khóa")
    )

    res = test_client.patch('/api/posts/1/unlocked')

    data = res.get_json()

    assert data["status"] == 400
    assert data["err_msg"] == "Bài viết không bị khóa, không thể mở khóa"


def test_unlocked_post_not_owner(test_client, mocker):
    mocker.patch(
        "blogapp.dao.unlock_post",
        return_value=(False, "Bài viết không phải của bạn, không thể mở khóa")
    )

    res = test_client.patch('/api/posts/1/unlocked')

    data = res.get_json()

    assert data["status"] == 400
    assert data["err_msg"] == "Bài viết không phải của bạn, không thể mở khóa"
