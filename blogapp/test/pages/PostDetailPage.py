from selenium.webdriver.common.by import By
from blogapp.test.pages.BasePage import BasePage


class PostDetailPage(BasePage):
    URL = 'http://127.0.0.1:5000/post-detail/'

    POST_TITLE = (By.CSS_SELECTOR, "h1.fw-bolder")
    COMMENT_COUNT = (By.ID, "comment-count")

    COMMENT_TEXTAREA = (By.ID, "comment-content")
    SUBMIT_COMMENT_BTN = (By.CSS_SELECTOR, "#comment-form button[type='submit']")
    COMMENT_SUCCESS_MSG = (By.ID, "comment-success")
    COMMENT_ERROR_MSG = (By.ID, "comment-error")
    LOGIN_TEXT = (By.LINK_TEXT, "đăng nhập")
    COMMENT_ITEMS = (By.CSS_SELECTOR, ".comment-item")
    REPLY_BUTTON = (By.CSS_SELECTOR, "#comment-list > div:nth-child(1) button[onclick*='showReplyForm']")
    REPLY_TEXT = (By.CSS_SELECTOR, "#comment-list > div:nth-child(1) .reply-textarea")
    REPLY_SUBMIT_BTN = (By.CSS_SELECTOR, "#comment-list > div:nth-child(1) button[onclick*='submitReply']")

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

    def click_reply_button(self, comment_id):
        locator = (By.CSS_SELECTOR, f".comment-item[data-comment-id='{comment_id}'] button[onclick*='showReplyForm']")
        self.click(*locator)

    def click_delete_comment_button(self, comment_id):
        locator = (By.CSS_SELECTOR, f".comment-item[data-comment-id='{comment_id}'] button[onclick*='deleteComment']")
        self.click(*locator)

    def click_login_text(self):
        self.click(*self.LOGIN_TEXT)

    def click_reply_button(self):
        self.click(*self.REPLY_BUTTON)

    def enter_reply_text(self, text):
        self.typing(*self.REPLY_TEXT, text)

    def submit_first_reply(self):
        self.click(*self.REPLY_SUBMIT_BTN)