import time
from blogapp.test.base import driver
from selenium.webdriver.common.by import By
from blogapp.test.pages.PostDetailPage import PostDetailPage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestCommentPost:

    def _setup_and_login(self, driver, post_id, username = "canhhuynh", password = "123456"):
        post_page = PostDetailPage(driver)
        post_page.open_page(post_id=post_id)
        time.sleep(2)

        post_page.click_login_text()
        time.sleep(1)

        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)

        post_page.open_page(post_id)
        time.sleep(2)
        return post_page

    def test_tc1_add_comment_success(self, driver):
        post_id = 1
        post_page = self._setup_and_login(driver, post_id)

        initial_count = post_page.get_comment_count()
        test_comment = "Test5"
        post_page.enter_comment(test_comment)
        post_page.submit_comment()

        # Đợi và chụp toast notification
        try:
            wait = WebDriverWait(driver, 5)
            toast = wait.until(EC.visibility_of_element_located((By.ID, "liveToast")))
            time.sleep(0.5)  # Đợi toast hiển thị hoàn toàn
            driver.save_screenshot("ActualResult/comment_success_msg.png")
        except:
            print("Toast không hiển thị hoặc đã biến mất")
            driver.save_screenshot("ActualResult/comment_success_msg.png")

        # Đợi page reload (sau 3 giây theo code JS)
        time.sleep(3.5)

        # Scroll xuống để thấy bình luận mới
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(1)
        driver.save_screenshot("ActualResult/comment_success.png")

        new_count = post_page.get_comment_count()

        assert new_count == initial_count + 1, "Số đếm bình luận không tăng lên!"
        assert test_comment in driver.page_source, "Không tìm thấy nội dung bình luận sau khi submit!"

    def test_tc2_add_reply_success(self, driver):
        post_id = 1
        post_page = self._setup_and_login(driver, post_id)

        post_page.click_reply_button()
        time.sleep(1)

        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(0.5)

        reply_content = "Đây là nội dung phản hồi cho bình luận đầu tiên"
        post_page.enter_reply_text(reply_content)
        post_page.submit_first_reply()

        try:
            wait = WebDriverWait(driver, 5)
            toast = wait.until(EC.visibility_of_element_located((By.ID, "liveToast")))
            time.sleep(0.5)
            driver.save_screenshot("ActualResult/reply_comment_success_msg.png")
        except:
            print("Toast không hiển thị hoặc đã biến mất")
            driver.save_screenshot("ActualResult/reply_comment_success_msg.png")

        time.sleep(3.5)

        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(1)

        assert reply_content in driver.page_source
        driver.save_screenshot("ActualResult/reply_comment_success.png")

    def test_tc3_spam_comment(self, driver):
        post_id = 1
        post_page = self._setup_and_login(driver, post_id)

        initial_count = post_page.get_comment_count()

        post_page.enter_comment("comment hợp lệ")
        post_page.submit_comment()

        try:
            wait = WebDriverWait(driver, 5)
            wait.until(EC.visibility_of_element_located((By.ID, "liveToast")))
            time.sleep(1)
        except:
            pass

        post_page.enter_comment("comment spam")
        post_page.submit_comment()

        try:
            wait = WebDriverWait(driver, 5)
            toast = wait.until(EC.visibility_of_element_located((By.ID, "liveToast")))
            time.sleep(0.5)
            driver.save_screenshot("ActualResult/spam_check_msg.png")
        except:
            print("Toast spam không hiển thị")
            driver.save_screenshot("ActualResult/spam_check_msg.png")

        time.sleep(2)
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(1)
        driver.save_screenshot("ActualResult/spam_check.png")

        time.sleep(1)
        assert post_page.get_comment_count() == initial_count + 1

    def test_tc4_full_comment(self, driver):
        post_id = 1
        post_page = self._setup_and_login(driver, post_id)

        initial_count = post_page.get_comment_count()

        post_page.enter_comment("comment4")
        post_page.submit_comment()
        time.sleep(11)

        post_page.enter_comment("comment5")
        post_page.submit_comment()
        time.sleep(1)

        post_page.enter_comment("comment6")
        post_page.submit_comment()

        try:
            wait = WebDriverWait(driver, 5)
            toast = wait.until(EC.visibility_of_element_located((By.ID, "liveToast")))
            time.sleep(0.5)
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(0.5)
            driver.save_screenshot("ActualResult/full_comment_err_msg.png")
        except:
            print("Toast full comment không hiển thị")
            driver.execute_script("window.scrollBy(0, 500);")
            driver.save_screenshot("ActualResult/full_comment_err_msg.png")

        time.sleep(2)
        driver.save_screenshot("ActualResult/full_comment.png")

        assert post_page.get_comment_count() == initial_count + 2

    def test_tc5_comment_lester_than_5_character(self, driver):
        post_id = 3
        post_page = self._setup_and_login(driver, post_id)

        initial_count = post_page.get_comment_count()

        short_comment = "Test"
        post_page.enter_comment(short_comment)
        post_page.submit_comment()
        time.sleep(2)
        driver.save_screenshot("ActualResult/comment_chars_invalid.png")
        assert initial_count == post_page.get_comment_count()