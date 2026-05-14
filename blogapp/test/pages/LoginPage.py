from selenium.webdriver.common.by import By
import time

class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.USERNAME_INPUT = (By.NAME, "username")
        self.PASSWORD_INPUT = (By.NAME, "password")
        self.SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")

    def login(self, base_url, username, password):
        self.driver.get(f"{base_url}/login")
        self.driver.find_element(*self.USERNAME_INPUT).send_keys(username)
        self.driver.find_element(*self.PASSWORD_INPUT).send_keys(password)
        self.driver.find_element(*self.SUBMIT_BUTTON).click()
        time.sleep(2)
