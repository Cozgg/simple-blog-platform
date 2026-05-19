import time
import os
import pytest
from selenium.webdriver.common.by import By

from blogapp import db, app
from blogapp.models import Post, Comment, User
from blogapp.test.pages.HomePage import HomePage
from blogapp.test.pages.LoginPage import LoginPage
from blogapp.test.pages.UserPostPage import UserPostPage
from blogapp.test.test_base import driver
from blogapp.test.base import test_app


def save_step_screenshot(driver, test_name, step):

    folder = f"screenshots/{test_name}"

    os.makedirs(folder, exist_ok=True)

    timestamp = int(time.time())

    path = f"{folder}/{step}_{timestamp}.png"

    driver.save_screenshot(path)

def create_post(
    title="Test Post Valid Title",
    user_id=1,
    comments_count=0,
    is_pinned=False,
    is_locked=False
):

    post = Post(
        title=title,
        content="Mock content",
        user_id=user_id,
        is_pinned=is_pinned,
        is_locked=is_locked
    )

    db.session.add(post)
    db.session.flush()

    comments = []

    for i in range(comments_count):
        c = Comment(
            content=f"Comment {i}",
            user_id=user_id,
            post_id=post.id
        )

        comments.append(c)

    db.session.add_all(comments)
    db.session.commit()

    return post

@pytest.fixture
def post_factory():

    created_posts = []

    def _create_post(
        username="admin",
        comments_count=0,
        is_pinned=False,
        is_locked=False
    ):

        with app.app_context():

            user = User.query.filter_by(
                username=username
            ).first()

            post = create_post(
                user_id=user.id,
                comments_count=comments_count,
                is_pinned=is_pinned,
                is_locked=is_locked
            )

            created_posts.append(post.id)

            return post

    yield _create_post

    with app.app_context():

        for post_id in created_posts:

            post = Post.query.get(post_id)

            if post:
                db.session.delete(post)

        db.session.commit()


def test_delete_post_success(driver, post_factory):
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

def test_admin_delete_post_user_success(driver, post_factory):
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

def test_modal_confirmed_post_with_10_comments(driver, post_factory):
    post = post_factory(username="canhhuynh", comments_count=11)

    login = LoginPage(driver=driver)
    login.open_page()
    login.login(username="canhhuynh", password="123456")

    home = HomePage(driver=driver)
    home.delete_post()

    is_modal_open = home.accept_delete_modal()

    assert is_modal_open is True

def test_delete_post_with_10_comments_success(driver, post_factory):
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


def test_cancel_delete_post_with_10_comments(driver, post_factory):
    post = post_factory(username="canhhuynh", comments_count=11)

    login = LoginPage(driver=driver)
    login.open_page()
    login.login(username="canhhuynh", password="123456")

    home = HomePage(driver=driver)

    home.delete_post()
    home.cancel_delete_modal()
    assert home.cancel_delete_modal() is True

def test_delete_button_hidden_for_other_post(driver, post_factory):
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

def test_delete_button_hidden_for_pinned_post(driver, post_factory):
    post1 = post_factory(username="ngocson", comments_count=11)
    post2 = post_factory(username="ngocson", is_pinned=True)
    login = LoginPage(driver=driver)
    login.open_page()
    login.login(username="ngocson", password="123456")
    time.sleep(1)
    user_post = UserPostPage(driver=driver)
    user_post.open_page()
    time.sleep(1)

    posts = user_post.get_all_post()
    for p in posts:
        is_pinned = p.find_element(By.CSS_SELECTOR, "[id^='pinned']")
        if is_pinned:
            del_btn = p.find_elements(By.ID, "delBtn")
            assert not del_btn

def test_delete_button_hidden_for_locked_post(driver, post_factory):
    post1 = post_factory(username="canhhuynh", comments_count=11)
    post2 = post_factory(username="canhhuynh", is_locked=True)

    login = LoginPage(driver=driver)
    login.open_page()
    login.login(username="canhhuynh", password="123456")
    time.sleep(1)
    user_post = UserPostPage(driver=driver)
    user_post.open_page()
    time.sleep(1)

    posts = user_post.get_all_post()
    for p in posts:
        is_locked = p.find_elements(By.CSS_SELECTOR, "[id^='locked']")
        if is_locked:
            del_btn = p.find_elements(By.ID, "delBtn")
            assert not del_btn






