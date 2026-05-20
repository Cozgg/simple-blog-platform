import time

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from blogapp.test.pages.BasePage import BasePage
import time as t


class PostDetailPage(BasePage):
    URL = 'http://127.0.0.1:5000/post-detail/'

    POST_TITLE = (By.CSS_SELECTOR, "h1.fw-bolder")
    COMMENT_COUNT = (By.ID, "comment-count")
    WARNING_MODAL = (By.ID, "globalConfirmModal")
    COMMENT_ITEMS = (By.CSS_SELECTOR, ".comment-item")
    COMMENT_TEXTAREA = (By.ID, "comment-content")
    SUBMIT_COMMENT_BTN = (By.CSS_SELECTOR, "#comment-form button[type='submit']")
    COMMENT_SUCCESS_MSG = (By.ID, "comment-success")
    COMMENT_ERROR_MSG = (By.ID, "comment-error")
    LOGIN_TEXT = (By.LINK_TEXT, "đăng nhập")
    REPLY_BUTTON = (By.CSS_SELECTOR, "#comment-list > div:nth-child(1) button[onclick*='showReplyForm']")
    REPLY_TEXT = (By.CSS_SELECTOR, "#comment-list > div:nth-child(1) .reply-textarea")
    REPLY_SUBMIT_BTN = (By.CSS_SELECTOR, "#comment-list > div:nth-child(1) button[onclick*='submitReply']")
    CLOSE_BTN = (By.CLASS_NAME, "btn-close")
    CONFIRM_DELETE_BTN = (By.ID, "btnConfirmYes")
    CANCEL_DELETE_BTN = (By.ID, "btnCancel")
    CONFIRM_MODAL = (By.ID, "globalConfirmModal")
    MODAL_CONFIRM_BTN = (By.ID, "btnConfirmYes")
    MODAL_CANCEL_BTN = (By.CSS_SELECTOR, "#globalConfirmModal .btn-secondary")
    MODAL_CLOSE_BTN = (By.CSS_SELECTOR, "#globalConfirmModal .btn-close")
    MODAL_TITLE = (By.ID, "confirmTitle")
    MODAL_BODY = (By.ID, "confirmMessage")
    TOAST_BODY = (By.ID, "toast-message")
    ALERT_LOCKED_POST = (By.CSS_SELECTOR, ".alert.alert-warning")

    def open_page(self, post_id=None):
        self.open(f"{self.URL}{post_id}")

    def get_post_title(self):
        return self.find(*self.POST_TITLE).text

    def get_comment_count(self):
        count_text = self.find(*self.COMMENT_COUNT).text
        return int(count_text) if count_text.isdigit() else 0

    def enter_comment(self, text):
        self.typing(*self.COMMENT_TEXTAREA, text)

    def submit_comment(self):
        self.click(*self.SUBMIT_COMMENT_BTN)

    def get_comment_validation_message(self):
        element = self.find(*self.COMMENT_TEXTAREA)
        return self.driver.execute_script("return arguments[0].validationMessage;", element)

    def click_delete_comment_button(self, comment_id):
        locator = (By.CSS_SELECTOR, f".comment-item[data-comment-id='{comment_id}'] button[onclick*='deleteComment']")
        self.click(*locator)

    def click_login_text(self):
        self.click(*self.LOGIN_TEXT)

    def click_first_reply_button(self):
        btn = self.find(*self.REPLY_BUTTON)
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", btn)
        time.sleep(0.5)
        self.click(*self.REPLY_BUTTON)

    def enter_reply_text(self, text):
        textarea = self.find(*self.REPLY_TEXT)
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", textarea)
        time.sleep(0.5)
        self.typing(*self.REPLY_TEXT, text)

    def submit_first_reply(self):
        self.click(*self.REPLY_SUBMIT_BTN)

    def click_del_comment_button(self, comment_id):
        btn = self.find(By.ID, f"del-btn-cmt-{comment_id}")
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", btn)
        time.sleep(0.5)
        btn.click()


    def click_delete_modal(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.WARNING_MODAL)
            )
            self.driver.find_element(*self.CONFIRM_DELETE_BTN).click()
            return True
        except TimeoutException:
            assert False, "Lỗi: Không hiển thị Modal xóa bình luận"

    def cancel_delete_modal(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.WARNING_MODAL)
            )
            self.driver.find_element(*self.CANCEL_DELETE_BTN).click()
            return True
        except TimeoutException:
            assert False, "Lỗi: Không hiển thị Modal xóa bình luận"

    def click_close_modal(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.WARNING_MODAL)
            )
            self.driver.find_element(*self.CLOSE_BTN).click()
            return True
        except TimeoutException as e:
            return False, f"Lỗi: {e}"

    def click_delete_first_comment_from_other_user(self):
        delete_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".comment-item button[onclick*='deleteComment']"))
        )
        delete_btn.click()
        # Use JavaScript to directly show the modal
        self.driver.execute_script("const modal = new bootstrap.Modal(document.getElementById('globalConfirmModal')); modal.show();")
        t.sleep(1)  # Wait for modal to appear

    def wait_for_confirm_modal(self):
        # Wait for modal to have Bootstrap 'show' class (indicates it's visible)
        WebDriverWait(self.driver, 10).until(
            lambda d: d.find_element(*self.CONFIRM_MODAL).get_attribute('class') is not None and 'show' in d.find_element(*self.CONFIRM_MODAL).get_attribute('class')
        )
        t.sleep(0.5)

    def get_modal_body_text(self):
        return self.find(*self.MODAL_BODY).text

    def click_confirm_delete(self):
        self.click(*self.MODAL_CONFIRM_BTN)

    def click_cancel_delete(self):
        self.click(*self.MODAL_CANCEL_BTN)

    def click_close_modal(self):
        self.click(*self.MODAL_CLOSE_BTN)
        
    def wait_for_modal_to_close(self):
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located(self.CONFIRM_MODAL))

    def get_toast_message(self):
        toast = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(self.TOAST_BODY))
        return toast.text

    def get_locked_alert(self):
        return self.find(*self.ALERT_LOCKED_POST).text