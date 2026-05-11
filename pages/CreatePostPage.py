from selenium.webdriver.common.by import By
from .BasePage import BasePage

class CreatePostPage(BasePage):
    TITLE_INPUT = (By.ID, "title")
    CONTENT_INPUT = (By.ID, "content")
    IMAGE_INPUT = (By.ID, "image")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    
    def __init__(self, driver):
        super().__init__(driver)
        self.url = "/create-post"

    def navigate(self, base_url):
        self.open(f"{base_url}{self.url}")

    def create_post(self, title, content, image_path=None):
        self.typing(*self.TITLE_INPUT, title)
        self.typing(*self.CONTENT_INPUT, content)
        if image_path:
            self.typing(*self.IMAGE_INPUT, image_path)
        self.click(*self.SUBMIT_BUTTON)