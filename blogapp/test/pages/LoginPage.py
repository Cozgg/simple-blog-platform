from selenium.webdriver.common.by import By
import time as t

from blogapp.test.pages.BasePage import BasePage


class LoginPage(BasePage):
    URL = 'http://127.0.0.1:5000/login'
    USERNAME = (By.ID, 'username')
    PASSWORD = (By.ID, 'pwd')
    BTN = (By.CSS_SELECTOR, '.container form button')

    def open_page(self, url=URL):
        self.open(url)

    def login(self, username, password):
        self.open_page()
        t.sleep(1)
        self.typing(*self.USERNAME, username)
        self.typing(*self.PASSWORD, password)
        self.click(*self.BTN)
        t.sleep(2)

    def fill_field(self, field_id, value):
        self.find(By.ID, field_id).send_keys(value)

    def submit(self):
        self.click(*self.BTN)
