import pytest
import time
import os
from blogapp.index import app
from blogapp import db
from blogapp.models import User, Post
from blogapp.test.pages.LoginPage import LoginPage
from blogapp.test.pages.HomePage import HomePage
from blogapp.test.base import driver

@pytest.fixture
def seed_10_posts():
    with app.app_context():
        user = User.query.filter_by(username='ngocson').first()
        
        if not user:
            pytest.skip("Không thấy user 'ngocson' trong cơ sở dữ liệu.")

        mock_posts = []
        for i in range(10):
            p = Post(
                title=f"Bài đăng thứ {i} để thực hiện bài test số 7 {int(time.time())}",
                content="Nội dung đủ dài 50 ký tự để lấp đầy DB okeokeokeoke",
                user_id=user.id
            )
            mock_posts.append(p)
            db.session.add(p)
        
        db.session.commit()
        
        yield 
        
        for p in mock_posts:
            post_to_delete = Post.query.get(p.id) 
            if post_to_delete:
                db.session.delete(post_to_delete)
        db.session.commit()


@pytest.mark.selenium
def test_tc1_create_post_success(driver):
    test_title = "Đi làm cty không anh xin cho "
    test_content = "Quê anh mảnh đất hữu tình, quê anh mảnh đất quê anh, quê anh mảnh đất quê anh, quê anh mảnh đất quê anh."

    login_page = LoginPage(driver)
    login_page.login("ngocson", "123456")

    home_page = HomePage(driver)
    home_page.open_page()
    home_page.open_create_modal()
    home_page.submit_post_ui(test_title, test_content)
    home_page.wait_for_success_and_refresh(test_title)

    # Check for success toast message
    success_msg = home_page.get_success_message()
    assert "Đăng bài viết thành công" in success_msg

    # Verify modal is closed
    assert test_title in driver.page_source

    driver.save_screenshot('test_tc1_create_post_success.png')


@pytest.mark.selenium
def test_tc2_create_post_fail_title_too_short(driver):
    login_page = LoginPage(driver)
    login_page.login("ngocson", "123456")

    home_page = HomePage(driver)
    home_page.open_page()
    home_page.open_create_modal()
    home_page.submit_post_ui("Ngắn", "Nội dung đủ dài để đăng bài viết okeokeokeokeokeoke")

    home_page.wait_for_inline_error()
    errors = home_page.get_inline_errors()

    assert 'title' in errors
    assert "Tiêu đề phải từ 10 đến 200 ký tự" in errors['title']

    driver.save_screenshot('test_tc2_title_too_short.png')


@pytest.mark.selenium
def test_tc3_create_post_fail_content_too_short(driver):
    login_page = LoginPage(driver)
    login_page.login("ngocson", "123456")

    home_page = HomePage(driver)
    home_page.open_page()

    home_page.open_create_modal()
    home_page.submit_post_ui("Tiêu đề đủ dài để đăng bài viết okeokeokeoke", "Ko đủ 50 ký tự")

    home_page.wait_for_inline_error()
    errors = home_page.get_inline_errors()

    assert 'content' in errors
    assert "Nội dung phải từ 50 đến 5000 ký tự" in errors['content']

    driver.save_screenshot('test_tc3_content_too_short.png')


@pytest.mark.selenium
def test_tc4_create_post_fail_both_invalid(driver):
    login_page = LoginPage(driver)
    login_page.login("ngocson", "123456")

    home_page = HomePage(driver)
    home_page.open_page()

    home_page.open_create_modal()
    home_page.submit_post_ui("Ngắn", "Ngắn")

    home_page.wait_for_inline_error()
    errors = home_page.get_inline_errors()

    assert 'title' in errors
    assert 'content' in errors
    assert "Tiêu đề phải từ 10 đến 200 ký tự" in errors['title']
    assert "Nội dung phải từ 50 đến 5000 ký tự" in errors['content']

    driver.save_screenshot('test_tc4_both_invalid.png')


@pytest.mark.selenium
def test_tc5_create_post_empty_fields(driver):
    login_page = LoginPage(driver)
    login_page.login("ngocson", "123456")

    home_page = HomePage(driver)
    home_page.open_page()

    home_page.open_create_modal()
    home_page.submit_post_ui("", "")

    home_page.wait_for_inline_error()
    errors = home_page.get_inline_errors()

    assert 'title' in errors
    assert 'content' in errors
    assert "Tiêu đề phải từ 10 đến 200 ký tự" in errors['title']
    assert "Nội dung phải từ 50 đến 5000 ký tự" in errors['content']

    driver.save_screenshot('test_tc5_empty_fields.png')


@pytest.mark.selenium
def test_tc6_duplicate_title_same_day(driver):
    login_page = LoginPage(driver)
    login_page.login("ngocson", "123456")

    home_page = HomePage(driver)
    home_page.open_page()

    test_title = f"Tiêu đề trùng lặp {int(time.time())}"
    valid_content = "Nội dung bài viết hợp lệ dài trên 50 ký tự để được đăng okeokeokeokeokeokeokeoke."

    home_page.open_create_modal()
    home_page.submit_post_ui(test_title, valid_content)
    home_page.wait_for_success_and_refresh(test_title)

    home_page.open_create_modal()
    home_page.submit_post_ui(test_title, valid_content)

    home_page.wait_for_post_error()
    error_msg = home_page.get_post_error_message()

    assert error_msg is not None
    assert ("đăng bài với tiêu đề này" in error_msg or "trùng" in error_msg.lower() or
            "giới hạn 10 bài" in error_msg or "đạt giới hạn" in error_msg.lower())

    driver.save_screenshot('test_tc6_duplicate_title.png')


@pytest.mark.selenium
def test_tc7_daily_limit_exceeded(driver, seed_10_posts):
    login_page = LoginPage(driver)
    login_page.login("ngocson", "123456")

    home_page = HomePage(driver)
    home_page.open_page()

    home_page.open_create_modal()
    
    home_page.submit_post_ui(
        f"Tiêu đề bài vượt giới hạn {int(time.time())}",
        "Nội dung bài viết hợp lệ dài trên 50 ký tự để được đăng okeokeokeokeokeokeokeoke."
    )

    home_page.wait_for_post_error()
    error_msg = home_page.get_post_error_message()

    assert error_msg is not None
    assert "giới hạn 10 bài" in error_msg or "đạt giới hạn" in error_msg.lower()

    driver.save_screenshot('test_tc7_daily_limit.png')


@pytest.mark.selenium
def test_tc8_create_post_with_image(driver):
    login_page = LoginPage(driver)
    login_page.login("ngocson", "123456")

    home_page = HomePage(driver)
    home_page.open_page()

    home_page.open_create_modal()

    test_title = f"Bài viết có ảnh {int(time.time())}"
    valid_content = "Nội dung bài viết hợp lệ dài trên 50 ký tự để được đăng okeokeokeokeokeokeokeoke."

    image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'img', 'lucasimg.jpg'))

    if not os.path.exists(image_path):
        pytest.skip("Không tìm thấy file ảnh test")

    home_page.submit_post_with_image(test_title, valid_content, image_path)
    home_page.wait_for_success_and_refresh(test_title)

    assert test_title in driver.page_source
    time.sleep(2)
    assert 'img' in driver.page_source or 'cloudinary' in driver.page_source.lower()

    driver.save_screenshot('test_tc8_create_post_with_image.png')
