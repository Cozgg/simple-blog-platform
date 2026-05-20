import time
import pytest
from blogapp import app, db
from blogapp.models import User, Comment, Post
from blogapp.test.pages.LoginPage import LoginPage
from blogapp.test.pages.PostDetailPage import PostDetailPage
from blogapp.test.test_base import driver
from blogapp.test.base import test_app

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

@pytest.fixture
def comment_factory():

    created_comments = []

    def _create_comment(
        content="Test comment",
        username="admin",
        post_id=1,
        parent_id=None
    ):

        with app.app_context():

            user = User.query.filter_by(
                username=username
            ).first()

            comment = Comment(
                content=content,
                user_id=user.id,
                post_id=post_id,
                parent_id=parent_id
            )

            db.session.add(comment)
            db.session.commit()

            created_comments.append(comment.id)

            return comment

    yield _create_comment

    with app.app_context():

        for comment_id in created_comments:

            comment = Comment.query.get(comment_id)

            if comment:
                db.session.delete(comment)

        db.session.commit()

@pytest.mark.selenium
class TestSelDeleteComment:
    def test_modal_delete_comment(self, driver, comment_factory):
        cmt1 = comment_factory(username="canhhuynh", content="Test Comment Factory")

        login = LoginPage(driver)
        login.open_page()
        login.login("canhhuynh", "123456")

        post_detail = PostDetailPage(driver)
        time.sleep(2)
        post_detail.open_page(post_id=1)
        driver.execute_script("window.scrollBy(0, 2000);")

        post_detail.click_del_comment_button(cmt1.id)
        is_modal_open = post_detail.click_delete_modal()

        assert is_modal_open is True

    def test_delete_comment_success(self, driver, comment_factory):
        cmt1 = comment_factory(username="canhhuynh", content="test comment")
        reply_cmt1 = comment_factory(username="canhhuynh", content="Test Comment Reply", parent_id=cmt1.id)

        login = LoginPage(driver)
        login.open_page()
        login.login("canhhuynh", "123456")

        post_detail = PostDetailPage(driver)
        time.sleep(1)
        post_detail.open_page(post_id=1)
        time.sleep(1)
        driver.execute_script("window.scrollBy(0, 5000);")
        comments_after_delete = post_detail.get_comment_count()
        post_detail.click_del_comment_button(cmt1.id)
        post_detail.click_delete_modal()

        toast_message = post_detail.get_toast_message()
        assert toast_message == "Đã xóa bình luận và 1 phản hồi liên quan."
        time.sleep(1)
        total_comment = post_detail.get_comment_count()
        assert comments_after_delete - 2 == total_comment

    def test_cancel_delete_button(self, driver, comment_factory):
        cmt1 = comment_factory(username="canhhuynh", content="Test Comment Factory")

        login = LoginPage(driver)
        login.open_page()
        login.login("canhhuynh", "123456")

        post_detail = PostDetailPage(driver)
        time.sleep(1)
        post_detail.open_page(post_id=1)
        time.sleep(1)
        total_comment = post_detail.get_comment_count()
        driver.execute_script("window.scrollBy(0, 5000);")
        post_detail.click_del_comment_button(cmt1.id)
        is_cancel_delete = post_detail.cancel_delete_modal()
        assert is_cancel_delete == True
        assert total_comment == 2

    def test_close_delete_button(self, driver, comment_factory):
        cmt1 = comment_factory(username="canhhuynh", content="test comment")

        login = LoginPage(driver)
        login.open_page()
        login.login("canhhuynh", "123456")

        post_detail = PostDetailPage(driver)
        time.sleep(1)
        post_detail.open_page(post_id=1)
        time.sleep(1)
        total_comment = post_detail.get_comment_count()
        driver.execute_script("window.scrollBy(0, 5000);")
        post_detail.click_del_comment_button(cmt1.id)
        time.sleep(1)
        post_detail.click_close_modal()
        time.sleep(2)
        after_comment = post_detail.get_comment_count()
        assert total_comment == after_comment

    def test_modal_delete_reply_comment(self, driver, comment_factory):
        cmt1 = comment_factory(username="canhhuynh", content="test comment")
        reply_cmt1 = comment_factory(username="canhhuynh", content="Test Comment Reply", parent_id=cmt1.id)

        login = LoginPage(driver)
        login.open_page()
        login.login("canhhuynh", "123456")

        post_detail = PostDetailPage(driver)
        time.sleep(1)
        post_detail.open_page(post_id=1)
        time.sleep(1)
        driver.execute_script("window.scrollBy(0, 5000);")
        post_detail.click_del_comment_button(reply_cmt1.id)
        is_cancel_delete = post_detail.click_delete_modal()
        assert is_cancel_delete == True

    def test_delete_reply_comment_success(self, driver, comment_factory):
        cmt1 = comment_factory(username="canhhuynh", content="test comment")
        reply_cmt1 = comment_factory(username="canhhuynh", content="Test Comment Reply", parent_id=cmt1.id)

        login = LoginPage(driver)
        login.open_page()
        login.login("canhhuynh", "123456")

        post_detail = PostDetailPage(driver)
        time.sleep(1)
        post_detail.open_page(post_id=1)
        total_comment = post_detail.get_comment_count()
        time.sleep(1)
        driver.execute_script("window.scrollBy(0, 5000);")
        post_detail.click_del_comment_button(reply_cmt1.id)
        post_detail.click_delete_modal()
        toast_message = post_detail.get_toast_message()
        assert toast_message == "Đã xóa phản hồi"

        time.sleep(1)
        after_delete_comment = post_detail.get_comment_count()
        assert total_comment - 1 == after_delete_comment

    def test_cancel_reply_delete_button(self, driver, comment_factory):
        cmt1 = comment_factory(username="canhhuynh", content="Test Comment Factory")
        reply_cmt1 = comment_factory(username="canhhuynh", content="Test Comment Reply", parent_id=cmt1.id)

        login = LoginPage(driver)
        login.open_page()
        login.login("canhhuynh", "123456")

        post_detail = PostDetailPage(driver)
        time.sleep(1)
        post_detail.open_page(post_id=1)
        time.sleep(1)
        total_comment = post_detail.get_comment_count()
        driver.execute_script("window.scrollBy(0, 5000);")
        post_detail.click_del_comment_button(reply_cmt1.id)
        is_cancel_delete = post_detail.cancel_delete_modal()
        assert is_cancel_delete == True
        time.sleep(1)
        after_cancel_total_comment = post_detail.get_comment_count()
        assert total_comment == after_cancel_total_comment

    def test_close_reply_delete_button(self, driver, comment_factory):
        cmt1 = comment_factory(username="canhhuynh", content="test comment")
        reply_cmt1 = comment_factory(username="canhhuynh", content="Test Comment Reply", parent_id=cmt1.id)

        login = LoginPage(driver)
        login.open_page()
        login.login("canhhuynh", "123456")

        post_detail = PostDetailPage(driver)
        time.sleep(1)
        post_detail.open_page(post_id=1)
        time.sleep(1)
        total_comment = post_detail.get_comment_count()
        driver.execute_script("window.scrollBy(0, 5000);")
        post_detail.click_del_comment_button(reply_cmt1.id)
        time.sleep(1)
        post_detail.click_close_modal()
        time.sleep(1)
        after_close_total_comment = post_detail.get_comment_count()
        assert total_comment == after_close_total_comment

    def test_owner_click_delete_shows_modal(self, driver, post_with_comment_factory):
        post = post_with_comment_factory(username="canhhuynh", comments_count=1)
        post_id = post.id

        login = LoginPage(driver)
        login.open_page()
        login.login("canhhuynh", "123456")

        post_page = PostDetailPage(driver)
        post_page.open_page(post_id)

        post_page.click_delete_first_comment_from_other_user()
        post_page.wait_for_confirm_modal()
        modal_text = post_page.get_modal_body_text()
        assert "Bạn có chắc chắn muốn xóa bình luận này?" in modal_text


    def test_1_owner_confirm_delete(self, driver, post_with_comment_factory):
        post = post_with_comment_factory(username="canhhuynh", comments_count=1, with_replies=True)
        post_id = post.id

        login = LoginPage(driver)
        login.open_page()
        login.login("canhhuynh", "123456")

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


    def test_2_owner_cancel_delete(self, driver, post_with_comment_factory):
        post = post_with_comment_factory(username="canhhuynh", comments_count=1)
        post_id = post.id

        login = LoginPage(driver)
        login.open_page()
        login.login("canhhuynh", "123456")

        post_page = PostDetailPage(driver)
        post_page.open_page(post_id)
        time.sleep(1)
        initial_count = post_page.get_comment_count()

        post_page.click_delete_first_comment_from_other_user()
        post_page.wait_for_confirm_modal()

        post_page.click_cancel_delete()
        post_page.wait_for_modal_to_close()

        new_count = post_page.get_comment_count()
        assert new_count == initial_count


    def test_tc3_3_owner_close_delete_modal(self, driver, post_with_comment_factory):
        post = post_with_comment_factory(username="canhhuynh", comments_count=1)
        post_id = post.id

        login = LoginPage(driver)
        login.open_page()
        login.login("canhhuynh", "123456")

        post_page = PostDetailPage(driver)
        time.sleep(1)
        post_page.open_page(post_id)
        initial_count = post_page.get_comment_count()

        post_page.click_delete_first_comment_from_other_user()
        post_page.wait_for_confirm_modal()

        post_page.click_close_modal()
        post_page.wait_for_modal_to_close()

        new_count = post_page.get_comment_count()
        assert new_count == initial_count


