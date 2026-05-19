from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:
    def __init__(self, driver):
        self.driver = driver

    TOAST_MESSAGE = (By.ID, "toast-message")
    def open(self, url):
        self.driver.get(url)

    def find(self, by, value):
        return self.driver.find_element(by, value)

    def finds(self, by, value):
        return self.driver.find_elements(by, value)

    def click(self, by, value):
        self.find(by, value).click()

    def typing(self, by, value, text):
        e = self.find(by, value)
        e.clear()
        self.driver.execute_script("arguments[0].value = arguments[1];", e, text)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", e)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", e)

    def get_toast_message(self):
        toast_element = WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located(self.TOAST_MESSAGE)
        )

        return toast_element.text