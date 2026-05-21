import time
import os
import pytest
from selenium.webdriver.common.by import By

from blogapp import db, app
from blogapp.models import Post, Comment, User
from blogapp.test.pages.ProfilePage import ProfilePage
from blogapp.test.pages.HomePage import HomePage
from blogapp.test.pages.LoginPage import LoginPage
from blogapp.test.test_base import driver
from blogapp.test.base import test_app
from blogapp.test.test_base import post_factory


def save_step_screenshot(driver, test_name, step):

    folder = f"screenshots/{test_name}"

    os.makedirs(folder, exist_ok=True)

    timestamp = int(time.time())

    path = f"{folder}/{step}_{timestamp}.png"

    driver.save_screenshot(path)


@pytest.mark.selenium
class TestSelDeletePost:
    def test_delete_post_success(self, driver, post_factory):
        post = post_factory()
        test_title = str(post.title)

        login = LoginPage(driver=driver)
        login.open_page()
        login.login(username="admin", password="admin123")

        home = HomePage(driver=driver)
        home.delete_post()
        msg = home.get_toast_message()
        assert msg == "Xóa thành công"
        current_titles = home.get_all_post_titles()
        assert test_title not in current_titles, "Lỗi: Bài viết vẫn còn hiển thị trên giao diện"

    def test_admin_delete_post_user_success(self, driver, post_factory):
        post = post_factory(username="canhhuynh")
        test_title = str(post.title)

        login = LoginPage(driver=driver)
        login.open_page()
        login.login(username="admin", password="admin123")

        home = HomePage(driver=driver)
        home.wait_for_home_page()
        home.delete_post()
        msg = home.get_toast_message()
        assert msg == "Xóa thành công"
        current_titles = home.get_all_post_titles()
        assert test_title not in current_titles, "Lỗi: Bài viết vẫn còn hiển thị trên giao diện"

    def test_modal_confirmed_post_with_10_comments(self, driver, post_factory):
        post = post_factory(username="canhhuynh", comments_count=11)

        login = LoginPage(driver=driver)
        login.open_page()
        login.login(username="canhhuynh", password="123456")

        home = HomePage(driver=driver)
        home.delete_post()

        is_modal_open = home.accept_delete_modal()

        assert is_modal_open is True

    def test_delete_post_with_10_comments_success(self, driver, post_factory):
        post = post_factory(username="canhhuynh", comments_count=11)
        test_title = str(post.title)

        login = LoginPage(driver=driver)
        login.open_page()
        login.login(username="canhhuynh", password="123456")

        home = HomePage(driver=driver)
        home.open_page()
        home.delete_post()
        home.accept_delete_modal()

        msg = home.get_toast_message()
        assert msg == "Xóa thành công"
        current_titles = home.get_all_post_titles()
        assert test_title not in current_titles, "Lỗi: Bài viết vẫn còn hiển thị trên giao diện"


    def test_cancel_delete_post_with_10_comments(self, driver, post_factory):
        post = post_factory(username="canhhuynh", comments_count=11)

        login = LoginPage(driver=driver)
        login.open_page()
        login.login(username="canhhuynh", password="123456")

        home = HomePage(driver=driver)

        home.delete_post()
        home.cancel_delete_modal()
        assert home.cancel_delete_modal() is True

    def test_delete_button_hidden_for_other_post(self, driver, post_factory):
        post1 = post_factory(username="canhhuynh", comments_count=11)
        post2 = post_factory(username="ngocson")
        login = LoginPage(driver=driver)
        login.open_page()
        login.login(username="canhhuynh", password="123456")

        home = HomePage(driver=driver)
        time.sleep(1)
        posts = home.get_all_post()
        for post in posts:
            author_element = post.find_element(By.CSS_SELECTOR, "[id^='author-post-']").text
            author_name = author_element.split("•")[0].replace("Tác giả:", "").strip()
            if author_name != "Thế Cảnh" :
                del_btn = post.find_elements(By.ID, "delBtn")
                assert not del_btn

    def test_delete_button_hidden_for_pinned_post(self, driver, post_factory):
        post1 = post_factory(username="ngocson", comments_count=11)
        post2 = post_factory(username="ngocson", is_pinned=True)
        login = LoginPage(driver=driver)
        login.open_page()
        login.login(username="ngocson", password="123456")
        time.sleep(1)
        user_post = ProfilePage(driver=driver)
        user_post.open_page(user_id=2)
        time.sleep(1)

        posts = user_post.get_all_post()
        for p in posts:
            is_pinned = p.find_elements(By.CSS_SELECTOR, "[id^='pinned']")
            if is_pinned:
                del_btn = p.find_elements(By.ID, "delBtn")
                assert not del_btn

    def test_delete_button_hidden_for_locked_post(self, driver, post_factory):
        post1 = post_factory(username="canhhuynh", comments_count=11)
        post2 = post_factory(username="canhhuynh", is_locked=True)

        login = LoginPage(driver=driver)
        login.open_page()
        login.login(username="canhhuynh", password="123456")
        time.sleep(1)
        user_post = ProfilePage(driver=driver)
        user_post.open_page(user_id=3)
        time.sleep(1)

        posts = user_post.get_all_post()
        for p in posts:
            is_locked = p.find_elements(By.CSS_SELECTOR, "[id^='locked']")
            if is_locked:
                del_btn = p.find_elements(By.ID, "delBtn")
                assert not del_btn






