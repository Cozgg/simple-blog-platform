from selenium.webdriver.common.by import By
from blogapp.test.pages.BasePage import BasePage
import time as t


class ProfilePage(BasePage):
    URL = 'http://127.0.0.1:5000/profile/'
    
    USER_NAME = (By.CSS_SELECTOR, "h4.fw-bold.text-dark")
    USER_USERNAME = (By.CSS_SELECTOR, "p.text-muted.small")
    USER_EMAIL = (By.CSS_SELECTOR, "p.text-muted.small")
    USER_AVATAR = (By.CSS_SELECTOR, "img.rounded-circle")
    POST_COUNT = (By.CSS_SELECTOR, "h3.fw-bold")
    POST_TITLE = (By.CSS_SELECTOR, "h5.card-title")
    POST_LINK = (By.CSS_SELECTOR, "a.btn-outline-dark")
    PAGINATION = (By.CSS_SELECTOR, "nav.pagination")
    NEXT_PAGE_BTN = (By.CSS_SELECTOR, "#next-page-btn a")
    PREV_PAGE_BTN = (By.CSS_SELECTOR, "#back-page-btn a")
    PAGE_LINKS = (By.CSS_SELECTOR, ".page-item .page-link")
    
    def open_page(self, user_id=None):
        if user_id:
            self.open(f"{self.URL}{user_id}")
        else:
            self.open(self.URL)
    
    def get_user_name(self):
        return self.find(*self.USER_NAME).text
    
    def get_user_info(self):
        info_text = self.find(*self.USER_USERNAME).text
        return info_text
    
    def get_post_count(self):
        count_text = self.find(*self.POST_COUNT).text
        return count_text
    
    def get_post_titles(self):
        posts = self.finds(*self.POST_TITLE)
        return [post.text for post in posts]
    
    def click_post_detail(self, index=0):
        links = self.finds(*self.POST_LINK)
        links[index].click()
    
    def has_pagination(self):
        try:
            self.find(*self.PAGINATION)
            return True
        except:
            return False
    
    def click_next_page(self):
        self.click(*self.NEXT_PAGE_BTN)
        t.sleep(1)
    
    def click_prev_page(self):
        self.click(*self.PREV_PAGE_BTN)
        t.sleep(1)
