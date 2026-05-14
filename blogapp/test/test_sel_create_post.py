import pytest
import time
from blogapp import app, db
from blogapp.models import Post
from blogapp.test.pages.LoginPage import LoginPage
from blogapp.test.test_base import driver

BASE_URL = "http://127.0.0.1:5000"


def test_tc1_create_post_success(driver):
    login_page = LoginPage(driver)
    login_page.login(BASE_URL, "ngocson", "123456")

    assert "logout" in driver.page_source.lower(), "Đăng nhập không thành công, không tìm thấy nút Logout"

    driver.get(f"{BASE_URL}/")

    test_title = f"Tiêu đề bài viết {int(time.time())}"
    valid_content = "Nội dung bài viết hợp lệ dài trên 50 ký tự để vượt qua bước kiểm tra."

    js_script = """
    const formData = new FormData();
    formData.append('title', arguments[0]);
    formData.append('content', arguments[1]);

    return fetch('/api/posts', {
        method: 'POST',
        body: formData
    }).then(res => res.json());
    """

    result = driver.execute_script(js_script, test_title, valid_content)

    assert result['status'] == 200, f"API call failed: {result}"
    assert result['msg'] == 'Đăng bài viết thành công', f"Unexpected message: {result['msg']}"

    time.sleep(1)

    with app.app_context():
        post_in_db = Post.query.filter_by(title=test_title).first()
        if post_in_db:
            db.session.delete(post_in_db)
            db.session.commit()

    assert driver.current_url == f"{BASE_URL}/"


def test_tc2_create_post_fail_title_too_short(driver):
    login_page = LoginPage(driver)
    login_page.login(BASE_URL, "ngocson", "123456")

    assert "logout" in driver.page_source.lower(), "Đăng nhập không thành công, không tìm thấy nút Logout"

    driver.get(f"{BASE_URL}/")

    js_script = """
    const formData = new FormData();
    formData.append('title', arguments[0]);
    formData.append('content', arguments[1]);

    return fetch('/api/posts', {
        method: 'POST',
        body: formData
    }).then(res => res.json());
    """

    result = driver.execute_script(js_script, "Ngắn", "Nội dung hợp lệ dài trên 50 ký tự...")

    assert result['status'] == 400, f"Expected 400, got {result['status']}"
    assert "Tiêu đề phải từ 10 đến 200 ký tự" in result['err_msg'], f"Unexpected error message: {result['err_msg']}"