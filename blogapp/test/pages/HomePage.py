from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from blogapp.test.pages.BasePage import BasePage
import time as t

class HomePage(BasePage):
    MODAL_TRIGGER = (By.CSS_SELECTOR, "button.btn-light[data-bs-target='#createPostModal']")
    MODAL = (By.ID, "createPostModal")
    TITLE_INPUT = (By.NAME, "title")
    CONTENT_INPUT = (By.NAME, "content")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    ERROR_MESSAGE = (By.ID, "post-error")
    SUCCESS_MESSAGE = (By.ID, "post-success")
    TITLE_ERROR = (By.ID, "title-error")
    CONTENT_ERROR = (By.ID, "content-error")

    def __init__(self, driver):
        super().__init__(driver)

    def open_create_modal(self):
        try:
            trigger = self.find(*self.MODAL_TRIGGER)
            self.driver.execute_script("arguments[0].click();", trigger)
        except:
            self.driver.execute_script("document.querySelector('[data-bs-target=\"#createPostModal\"]').click();")
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.MODAL))
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.TITLE_INPUT))

    def submit_post_ui(self, title, content):
        self.typing(*self.TITLE_INPUT, title)
        self.typing(*self.CONTENT_INPUT, content)
        self.driver.execute_script("arguments[0].click();", self.find(*self.SUBMIT_BUTTON))

    def submit_post_with_image(self, title, content, image_path):
        self.typing(*self.TITLE_INPUT, title)
        self.typing(*self.CONTENT_INPUT, content)

        file_input = self.find(By.NAME, "image")
        file_input.send_keys(image_path)

        self.driver.execute_script("arguments[0].click();", self.find(*self.SUBMIT_BUTTON))

    def wait_for_success_and_refresh(self, post_title):
        WebDriverWait(self.driver, 10).until(EC.invisibility_of_element_located(self.MODAL))
        WebDriverWait(self.driver, 10).until(lambda d: post_title in d.page_source)

    def wait_for_inline_error(self):
        t.sleep(0.5)
        title_error = self.find(*self.TITLE_ERROR)
        content_error = self.find(*self.CONTENT_ERROR)

        has_error = False
        if title_error and title_error.is_displayed():
            has_error = True
        if content_error and content_error.is_displayed():
            has_error = True

        if not has_error:
            WebDriverWait(self.driver, 10).until(
                lambda d: (
                    (title_error and title_error.is_displayed()) or
                    (content_error and content_error.is_displayed())
                )
            )

    def get_inline_errors(self):
        title_error = self.find(*self.TITLE_ERROR)
        content_error = self.find(*self.CONTENT_ERROR)
        errors = {}
        if title_error and title_error.is_displayed():
            errors['title'] = title_error.text
        if content_error and content_error.is_displayed():
            errors['content'] = content_error.text
        return errors

    def wait_for_post_error(self):
        t.sleep(0.5)
        error_element = self.find(*self.ERROR_MESSAGE)
        if error_element and not error_element.is_displayed():
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.ERROR_MESSAGE))

    def get_post_error_message(self):
        error_element = self.find(*self.ERROR_MESSAGE)
        if error_element and error_element.is_displayed():
            return error_element.text
        return None
