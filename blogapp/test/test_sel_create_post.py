import pytest
import time
import os
from datetime import date, datetime
from blogapp import app, db
from blogapp.models import Post, User
from blogapp.test.pages.LoginPage import LoginPage
from blogapp.test.pages.HomePage import HomePage
from blogapp.test.test_base import driver

@pytest.mark.selenium
class TestSelCreatePost:
    def test_tc1_create_post_success(driver):
        login_page = LoginPage(driver)
        login_page.open_page()
        login_page.login("ngocson", "123456")

        home_page = HomePage(driver)
        home_page.open_page()
        home_page.open_create_modal()

        test_title = f"Tiêu đề bài viết {int(time.time())}"
        valid_content = "Nội dung bài viết hợp lệ dài trên 50 ký tự để được đăng okeokeokeokeokeokeokeoke."

        home_page.submit_post_ui(test_title, valid_content)
        home_page.wait_for_success_and_refresh(test_title)
        assert test_title in driver.page_source

        with app.app_context():
            post_in_db = Post.query.filter_by(title=test_title).first()
            if post_in_db:
                db.session.delete(post_in_db)
                db.session.commit()


    def test_tc2_create_post_fail_title_too_short(driver):
        login_page = LoginPage(driver)
        login_page.open_page()
        login_page.login("ngocson", "123456")

        home_page = HomePage(driver)
        home_page.open_page()
        home_page.open_create_modal()
        home_page.submit_post_ui("Ngắn", "Nội dung đủ dài để đăng bài viết okeokeokeokeokeoke")

        home_page.wait_for_inline_error()
        errors = home_page.get_inline_errors()

        assert 'title' in errors
        assert "Tiêu đề phải từ 10 đến 200 ký tự" in errors['title']



    def test_tc3_create_post_fail_content_too_short(driver):
        login_page = LoginPage(driver)
        login_page.open_page()
        login_page.login("ngocson", "123456")

        home_page = HomePage(driver)
        home_page.open_page()

        home_page.open_create_modal()
        home_page.submit_post_ui("Tiêu đề đủ dài để đăng bài viết okeokeokeoke", "Ko đủ 50 ký tự")

        home_page.wait_for_inline_error()
        errors = home_page.get_inline_errors()

        assert 'content' in errors
        assert "Nội dung phải từ 50 đến 5000 ký tự" in errors['content']



    def test_tc4_create_post_fail_both_invalid(driver):
        login_page = LoginPage(driver)
        login_page.open_page()
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



    def test_tc5_create_post_empty_fields(driver):
        login_page = LoginPage(driver)
        login_page.open_page()
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



    def test_tc6_duplicate_title_same_day(driver):
        login_page = LoginPage(driver)
        login_page.open_page()
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


        with app.app_context():
            post_in_db = Post.query.filter_by(title=test_title).first()
            if post_in_db:
                db.session.delete(post_in_db)
                db.session.commit()


    def test_tc7_daily_limit_exceeded(driver):
        login_page = LoginPage(driver)
        login_page.open_page()
        login_page.login("ngocson", "123456")

        home_page = HomePage(driver)
        home_page.open_page()
        with app.app_context():
            today = date.today()
            current_count = Post.query.filter(
                Post.user_id == 2,
                db.func.date(Post.created_date) == today
            ).count()

        posts_to_create = 10 - current_count
        if posts_to_create > 0:
            with app.app_context():
                user = User.query.get(2)
                for i in range(posts_to_create):
                    post = Post(
                        title=f"Bài viết test {i} - {int(time.time())}",
                        content=f"Nội dung bài viết hợp lệ dài trên 50 ký tự để được đăng okeokeokeokeokeokeokeoke cho bài test số {i}.",
                        user_id=2,
                        created_date=datetime.now()
                    )
                    db.session.add(post)
                db.session.commit()

        home_page.open_create_modal()
        home_page.submit_post_ui(
            f"Tiêu đề bài vượt giới hạn {int(time.time())}",
            "Nội dung bài viết hợp lệ dài trên 50 ký tự để được đăng okeokeokeokeokeokeokeoke."
        )

        home_page.wait_for_post_error()
        error_msg = home_page.get_post_error_message()

        assert error_msg is not None
        assert "giới hạn 10 bài" in error_msg or "đạt giới hạn" in error_msg.lower()


        with app.app_context():
            today = date.today()
            test_posts = Post.query.filter(
                Post.user_id == 2,
                db.func.date(Post.created_date) == today,
                Post.title.like('%test%')
            ).all()
            for post in test_posts:
                db.session.delete(post)
            db.session.commit()


    def test_tc8_create_post_with_image(driver):
        login_page = LoginPage(driver)
        login_page.open_page()
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


        with app.app_context():
            post_in_db = Post.query.filter_by(title=test_title).first()
            if post_in_db:
                db.session.delete(post_in_db)
                db.session.commit()