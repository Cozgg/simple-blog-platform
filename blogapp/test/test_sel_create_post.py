import pytest
import time
from blogapp import app, db
from blogapp.models import Post
from blogapp.test.pages.LoginPage import LoginPage
from blogapp.test.pages.HomePage import HomePage
from blogapp.test.test_base import driver

BASE_URL = "http://127.0.0.1:5000"


def test_tc1_create_post_success(driver):
    login_page = LoginPage(driver)
    login_page.login("ngocson", "123456")

    home_page = HomePage(driver)
    home_page.open(f"{BASE_URL}/")

    home_page.open_create_modal()

    test_title = f"Tiêu đề bài viết {int(time.time())}"
    valid_content = "Nội dung bài viết hợp lệ dài trên 50 ký tự để vượt qua bước kiểm tra."

    home_page.submit_post_ui(test_title, valid_content)
    home_page.wait_for_success_and_refresh(test_title)

    assert test_title in driver.page_source

    driver.save_screenshot('test_create_post_success.png')

    with app.app_context():
        post_in_db = Post.query.filter_by(title=test_title).first()
        if post_in_db:
            db.session.delete(post_in_db)
            db.session.commit()


def test_tc2_create_post_fail_title_too_short(driver):
    login_page = LoginPage(driver)
    login_page.login("ngocson", "123456")

    assert "logout" in driver.page_source.lower(), "Đăng nhập không thành công, không tìm thấy nút Logout"

    home_page = HomePage(driver)
    home_page.open(f"{BASE_URL}/")

    home_page.open_create_modal()
    home_page.submit_post_ui("Ngắn", "Nội dung hợp lệ dài trên 50 ký tự...")

    error_msg = home_page.wait_for_error_message()
    assert "Tiêu đề phải từ 10 đến 200 ký tự" in error_msg

    driver.save_screenshot('test_create_post_fail.png')