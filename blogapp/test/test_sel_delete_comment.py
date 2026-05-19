import time
import pytest
from blogapp import app, db
from blogapp.models import User, Comment
from blogapp.test.pages.LoginPage import LoginPage
from blogapp.test.pages.PostDetailPage import PostDetailPage
from blogapp.test.test_base import driver
from blogapp.test.base import test_app

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
        is_cancel_delete = post_detail.click_close_modal()
        assert is_cancel_delete == True
        assert total_comment == 2

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
        assert total_comment == 3

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
        is_cancel_delete = post_detail.click_close_modal()
        assert is_cancel_delete == True
        assert total_comment == 3


