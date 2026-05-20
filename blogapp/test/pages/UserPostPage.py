from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from blogapp.test.pages.BasePage import BasePage
import time


class UserPostPage(BasePage):

    URL = 'http://127.0.0.1:5000/user-posts'
    POST_CONTAINER = (By.ID, "post-list-container")
    POST_ITEM = (By.CSS_SELECTOR, "[id^='post-']")

    def __init__(self, driver):
        super().__init__(driver)

    def open_page(self, url=URL):
        self.open(url)

    def get_all_post(self):
        while True:
            self.driver.execute_script('window.scrollTo(0, 5000)')
            time.sleep(1)
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