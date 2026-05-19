import pytest
import time
from blogapp.index import app
from blogapp import db
from blogapp.models import User, Post, Comment
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from blogapp.test.pages.LoginPage import LoginPage
from blogapp.test.pages.PostDetailPage import PostDetailPage
from blogapp.test.base import driver


def create_post_with_comments(
    title="Test Post Valid Title",
    user_id=1,
    comments_count=0,
    is_pinned=False,
    is_locked=False,
    with_replies=False
):
    post = Post(
        title=title,
        content="Mock content for delete comment test",
        user_id=user_id,
        is_pinned=is_pinned,
        is_locked=is_locked
    )

    db.session.add(post)
    db.session.flush()

    comments = []

    for i in range(comments_count):
        c = Comment(
            content=f"Comment {i} for delete test",
            user_id=user_id,
            post_id=post.id
        )

        comments.append(c)

    db.session.add_all(comments)
    db.session.flush()

    if with_replies and comments_count > 0:
        replies_count = 2 
        for i in range(replies_count):
            reply = Comment(
                content=f"Reply {i} to comment 0",
                user_id=user_id,
                post_id=post.id,
                parent_id=comments[0].id
            )
            comments.append(reply)

    db.session.commit()

    return post


@pytest.fixture
def post_with_comment_factory():
    created_posts = []

    def _create_post(
        username="ngocson",
        comments_count=1,
        is_pinned=False,
        is_locked=False,
        with_replies=False
    ):
        with app.app_context():
            user = User.query.filter_by(username=username).first()

            post = create_post_with_comments(
                user_id=user.id,
                comments_count=comments_count,
                is_pinned=is_pinned,
                is_locked=is_locked,
                with_replies=with_replies
            )

            created_posts.append(post.id)

            return post

    yield _create_post

    with app.app_context():
        for post_id in created_posts:
            post = Post.query.get(post_id)
            if post:
                Comment.query.filter_by(post_id=post_id).delete()
                db.session.delete(post)
        db.session.commit()


@pytest.fixture
def seed_post_with_other_user_comment():
    yield 1


def test_tc3_owner_click_delete_shows_modal(driver, post_with_comment_factory):
    post = post_with_comment_factory(username="ngocson", comments_count=1)
    post_id = post.id

    login = LoginPage(driver)
    login.login("ngocson", "123456")

    post_page = PostDetailPage(driver)
    post_page.open_page(post_id)

    post_page.click_delete_first_comment_from_other_user()
    post_page.wait_for_confirm_modal()
    modal_text = post_page.get_modal_body_text()
    assert "Bạn có chắc chắn muốn xóa bình luận này?" in modal_text

    driver.save_screenshot('test_tc3_delete_modal_shows.png')


def test_tc3_1_owner_confirm_delete(driver, post_with_comment_factory):
    post = post_with_comment_factory(username="ngocson", comments_count=1, with_replies=True)
    post_id = post.id

    login = LoginPage(driver)
    login.login("ngocson", "123456")

    post_page = PostDetailPage(driver)
    post_page.open_page(post_id)

    initial_count = post_page.get_comment_count()

    post_page.click_delete_first_comment_from_other_user()
    post_page.wait_for_confirm_modal()

    post_page.click_confirm_delete()

    toast_msg = post_page.get_toast_message()
    assert "Đã xóa bình luận" in toast_msg
    assert "phản hồi liên quan" in toast_msg

    time.sleep(1.5)

    new_count = post_page.get_comment_count()
    assert new_count < initial_count
    assert new_count == 0

    driver.save_screenshot('test_tc3_1_confirm_delete.png')


def test_tc3_2_owner_cancel_delete(driver, post_with_comment_factory):
    post = post_with_comment_factory(username="ngocson", comments_count=1)
    post_id = post.id

    login = LoginPage(driver)
    login.login("ngocson", "123456")

    post_page = PostDetailPage(driver)
    post_page.open_page(post_id)

    initial_count = post_page.get_comment_count()

    post_page.click_delete_first_comment_from_other_user()
    post_page.wait_for_confirm_modal()

    post_page.click_cancel_delete()
    post_page.wait_for_modal_to_close()

    new_count = post_page.get_comment_count()
    assert new_count == initial_count

    driver.save_screenshot('test_tc3_2_cancel_delete.png')


def test_tc3_3_owner_close_delete_modal(driver, post_with_comment_factory):
    post = post_with_comment_factory(username="ngocson", comments_count=1)
    post_id = post.id

    login = LoginPage(driver)
    login.login("ngocson", "123456")

    post_page = PostDetailPage(driver)
    post_page.open_page(post_id)

    initial_count = post_page.get_comment_count()

    post_page.click_delete_first_comment_from_other_user()
    post_page.wait_for_confirm_modal()

    post_page.click_close_modal()
    post_page.wait_for_modal_to_close()

    new_count = post_page.get_comment_count()
    assert new_count == initial_count

    driver.save_screenshot('test_tc3_3_close_delete_modal.png')
