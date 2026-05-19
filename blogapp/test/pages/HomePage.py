import time

from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from blogapp.test.pages.BasePage import BasePage
import time as t

class HomePage(BasePage):
    URL = 'http://127.0.0.1:5000'
    MODAL_TRIGGER = (By.CSS_SELECTOR, "button.btn-light[data-bs-target='#createPostModal']")
    MODAL = (By.ID, "createPostModal")
    TITLE_INPUT = (By.NAME, "title")
    CONTENT_INPUT = (By.NAME, "content")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    ERROR_MESSAGE = (By.ID, "post-error")
    DELETE_POST_BUTTON = (By.CLASS_NAME, "btn-danger")
    POST_CONTAINER = (By.ID, "post-list-container")
    POST_ITEM = (By.CSS_SELECTOR, "[id^='post-']")
    POST_TITLE = (By.CLASS_NAME, "card-title")
    CREATE_POST_BUTTON = (
        By.CSS_SELECTOR,
        "button[data-bs-target='#createPostModal']"
    )
    WARNING_MODAL = (By.ID, "globalConfirmModal")
    CONFIRM_DELETE_BTN = (By.ID, "btnConfirmYes")
    CANCEL_DELETE_BTN = (By.ID, "btnCancel")
    SUCCESS_MESSAGE = (By.ID, "post-success")
    TITLE_ERROR = (By.ID, "title-error")
    CONTENT_ERROR = (By.ID, "content-error")

    def __init__(self, driver):
        super().__init__(driver)

    def open_page(self, url=URL):
        self.open(url)

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


    def wait_for_home_page(self):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(
                self.CREATE_POST_BUTTON
            )
        )


    def delete_post(self):
        time.sleep(2)
        post_container = self.find(By.ID, "post-list-container")
        posts = post_container.find_elements(
            By.CSS_SELECTOR,
            "[id^='post-']"
        )

        latest_post = posts[0]
        delete_btn = latest_post.find_element(*self.DELETE_POST_BUTTON)
        delete_btn.click()


    def get_all_post_titles(self):
        self.driver.implicitly_wait(2)

        post_container = self.find(*self.POST_CONTAINER)
        posts = post_container.find_elements(*self.POST_ITEM)

        return [p.find_element(*self.POST_TITLE).text for p in posts]


    def get_all_post(self):
        while True:
            self.driver.execute_script('window.scrollTo(0, 5000)')
            time.sleep(0.5)
            post_container = self.find(*self.POST_CONTAINER)
            posts = post_container.find_elements(*self.POST_ITEM)
            result = [p for p in posts]
            try:
                next_page_li = self.find(By.ID, "next-page-btn")

                if "disabled" in next_page_li.get_attribute("class"):
                    return result

                next_link = next_page_li.find_element(By.TAG_NAME, "a")
                next_link.click()
                time.sleep(1)
            except NoSuchElementException:
                return result


    def accept_delete_modal(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.WARNING_MODAL)
            )
            self.driver.find_element(*self.CONFIRM_DELETE_BTN).click()
            return True
        except TimeoutException:
            assert False, "Lỗi: Không hiển thị Modal cảnh báo khi xóa bài > 10 bình luận"


    def cancel_delete_modal(self):
        try:
            WebDriverWait(self.driver, 3).until(
                EC.visibility_of_element_located(self.WARNING_MODAL)
            )
            self.driver.find_element(*self.CANCEL_DELETE_BTN).click()
            return True
        except TimeoutException:
            assert False, "Lỗi: Không hiển thị Modal cảnh báo khi xóa bài > 10 bình luận"
