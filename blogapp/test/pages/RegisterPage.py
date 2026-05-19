from selenium.webdriver.common.by import By
from blogapp.test.pages.BasePage import BasePage


class RegisterPage(BasePage):
    URL = 'http://127.0.0.1:5000/register'

    NAME     = (By.ID, 'name')
    USERNAME = (By.ID, 'username')
    EMAIL    = (By.ID, 'email')
    PASSWORD = (By.ID, 'pwd')
    CONFIRM  = (By.ID, 'confirm')
    AVATAR   = (By.ID, 'avatar')
    BTN      = (By.CSS_SELECTOR, 'button.btn-danger')
    ERR_MSG  = (By.CSS_SELECTOR, 'div.alert.alert-danger')

    def open_page(self, url=URL):
        self.open(url)

    def fill_form(self, name, username, email, password, confirm, avatar_path=None):
        self.typing(*self.NAME, name)
        self.typing(*self.USERNAME, username)
        self.typing(*self.EMAIL, email)
        self.typing(*self.PASSWORD, password)
        self.typing(*self.CONFIRM, confirm)
        if avatar_path:
            self.find(*self.AVATAR).send_keys(avatar_path)

    def submit(self):
        self.click(*self.BTN)

    def register(self, name, username, email, password, confirm, avatar_path=None):
        self.fill_form(name, username, email, password, confirm, avatar_path)
        self.submit()

    def bypass_required(self, field_id):
        self.driver.execute_script(
            f"document.getElementById('{field_id}').removeAttribute('required');"
        )

    def bypass_all_required(self):
        for fid in ('name', 'username', 'email', 'pwd', 'confirm', 'avatar'):
            self.bypass_required(fid)

    def fill_field(self, field_id, value):
        self.find(By.ID, field_id).send_keys(value)

    def get_error_message(self):
        elements = self.finds(*self.ERR_MSG)
        if elements and elements[0].is_displayed():
            return elements[0].text
        return None
