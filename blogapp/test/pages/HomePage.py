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
        self.driver.execute_script("document.getElementById('createPostForm').noValidate = true;")
        self.driver.execute_script("arguments[0].click();", self.find(*self.SUBMIT_BUTTON))

    def wait_for_success_and_refresh(self, post_title):
        WebDriverWait(self.driver, 10).until(EC.invisibility_of_element_located(self.MODAL))
        WebDriverWait(self.driver, 10).until(lambda d: post_title in d.page_source)

    def wait_for_error_message(self):
        t.sleep(0.5)
        error_element = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.ERROR_MESSAGE))
        return error_element.text
