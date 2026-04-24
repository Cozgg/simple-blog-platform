from pytest_mock import mocker
from blogapp.test.base import test_app, test_client, test_session
from blogapp.models import Post, Comment, User
from datetime import datetime

def mock_login(mocker):
    class FakeUser:
        is_authenticated = True
        id = 1

    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())

def test_comment_success(test_client, mocker):
    mock_login(mocker)
    save_comment_mock = mocker.patch("blogapp.dao.save_comment")

    res = test_client.post(
        "/api/comments",
        json={
            "content": "Đây là bình luận hợp lê",
            "post_id": 2
        }
    )

    data = res.get_json()
    assert data["status"] == 201
    assert data["msg"] == "Đã đăng tải thành công bình luận"

    save_comment_mock.assert_called_once()

def test_prevent_comment_spam(test_client,test_session, mocker):
    mock_login(mocker)
    mocker.patch("blogapp.dao.save_comment", side_effect=PermissionError("Vui lòng đợi sau"))

    p1 = Post(title='Post Open', content='Content 1', user_id=1, is_locked=False)
    test_session.add(p1)
    test_session.commit()
    c1 = Comment(content="Comment post open 1", user_id=1, post_id=1, parent_id=None, created_date=datetime.now())
    test_session.add(c1)
    test_session.commit()

    res = test_client.post(
        "/api/comments",
        json={
            "content": "Đây là bình luận hợp lê",
            "post_id":  p1.id
        }
    )

    data = res.get_json()
    assert data['status'] == 400
    assert 'Vui lòng đợi sau' in data['err_msg']


def test_prevent_comment_not_enough_character(test_client, mocker):
    mock_login(mocker)

    res = test_client.post(
        "/api/comments",
        json={
            "content": "ab",
            "post_id": 2
        }
    )
    data = res.get_json()

    assert data['status'] == 400
    assert 'Nội dung của bình luận tối thiểu 5 kí tự' in data['err_msg']

def test_prevent_comment_post_locked_or_null_post(test_client,test_session, mocker):
    mock_login(mocker)
    mocker.patch("blogapp.dao.save_comment", side_effect=PermissionError("Bài viết này đã bị khóa bình luận"))

    p1 = Post(title='Post Open', content='Content 1', user_id=1, is_locked=True)
    test_session.add(p1)
    test_session.commit()

    res = test_client.post(
        "/api/comments",
        json={
            "content": "Đây là comment vào post bị khóa",
            "post_id": p1.id
        }
    )
    data = res.get_json()

    assert data['status'] == 400
    assert 'Bài viết này đã bị khóa bình luận' in data['err_msg']

    mocker.patch("blogapp.dao.save_comment", side_effect=PermissionError("Bài viết không tồn tại"))
    test_session.delete(p1)
    test_session.commit()
    res = test_client.post(
        "/api/comments",
        json={
            "content": "Đây là comment vào post không tồn tại",
            "post_id": p1.id
        }
    )
    data = res.get_json()
    assert data['status'] == 400
    assert 'Bài viết không tồn tại' in data['err_msg']

def test_reached_comment_limit(test_client,test_session, mocker):
    mock_login(mocker)
    mocker.patch("blogapp.dao.save_comment", side_effect=PermissionError("Bạn đã đạt đến giới hạn bình luận cho bài viết này"))
    p1 = Post(title='Post Open', content='Content 1', user_id=1, is_locked=True)
    test_session.add(p1)
    test_session.commit()

    c1 = Comment(content="Comment post open 1", user_id=1, post_id=p1.id,
                 created_date=datetime.strptime("2026-03-28 20:00:05", "%Y-%m-%d %H:%M:%S"))
    c2 = Comment(content="Comment post open 1", user_id=1, post_id=p1.id,
                 created_date=datetime.strptime("2026-03-28 22:00:05", "%Y-%m-%d %H:%M:%S"))
    c3 = Comment(content="Comment post open 1", user_id=1, post_id=p1.id,
                 created_date=datetime.strptime("2026-03-28 22:15:20", "%Y-%m-%d %H:%M:%S"))
    c4 = Comment(content="Comment post open 1", user_id=1, post_id=p1.id,
                 created_date=datetime.strptime("2026-03-28 22:30:00", "%Y-%m-%d %H:%M:%S"))
    c5 = Comment(content="Comment post open 1", user_id=1, post_id=p1.id,
                 created_date=datetime.strptime("2026-03-28 22:45:30", "%Y-%m-%d %H:%M:%S"))
    test_session.add_all([c1,c2,c3,c4,c5])
    test_session.commit()

    res = test_client.post(
        "/api/comments",
        json={
            "content": "Đây là comment không hợp lệ thứ 6",
            "post_id": p1.id
        }
    )

    data = res.get_json()
    assert data['status'] == 400
    assert 'Bạn đã đạt đến giới hạn bình luận cho bài viết này' in data['err_msg']

def test_comment_system_error(test_client, mocker):
    mock_login(mocker)

    mocker.patch("blogapp.dao.save_comment",side_effect=Exception("Lỗi BD"))

    res = test_client.post(
        "/api/comments",
        json={
            "content": "Đây là bình luận hợp lệ",
            "post_id": 2
        }
    )

    data = res.get_json()
    assert data["status"] == 500
    assert data["err_msg"] == "Lỗi hệ thống không xác định"