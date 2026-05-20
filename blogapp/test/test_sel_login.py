import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from blogapp.test.test_base import driver
from blogapp.test.pages.LoginPage import LoginPage

BASE_URL = "http://127.0.0.1:5000"
LOGIN_URL = f"{BASE_URL}/login"
HOME_URL = f"{BASE_URL}/"

LOGOUT_LINK = (By.CSS_SELECTOR, "a[href='/logout']")
LOGIN_LINK = (By.CSS_SELECTOR, "a[href='/login']")


@pytest.mark.selenium
class TestLoginSuccess:
    def test_login_success(self, driver):
        login_page = LoginPage(driver)
        login_page.open_page()
        login_page.login("ngocson", "123456")
        time.sleep(2)
        assert driver.current_url == HOME_URL
        logout_links = driver.find_elements(*LOGOUT_LINK)
        assert len(logout_links) > 0
        driver.save_screenshot("ActualResult/login_success_user.png")
        assert "ngocson" in driver.page_source

    def test_login_then_logout_redirects_to_login(self, driver):
        login_page = LoginPage(driver)
        login_page.open_page()
        login_page.login("ngocson", "123456")
        time.sleep(2)

        driver.get(f"{BASE_URL}/logout")
        time.sleep(1)

        assert "/login" in driver.current_url
        driver.save_screenshot("ActualResult/login_logout_redirect.png")

@pytest.mark.selenium
class TestLoginFailure:
    def test_wrong_password(self, driver):
        login_page = LoginPage(driver)
        login_page.open_page()
        login_page.login("ngocson", "SaiMatKhau99")
        time.sleep(2)

        login_links = driver.find_elements(*LOGIN_LINK)
        assert len(login_links) > 0

        driver.save_screenshot("ActualResult/login_wrong_password.png")

    def test_wrong_username(self, driver):
        login_page = LoginPage(driver)
        login_page.open_page()
        login_page.login("khong_ton_tai", "123456")
        time.sleep(2)

        login_links = driver.find_elements(*LOGIN_LINK)
        assert len(login_links) > 0

        driver.save_screenshot("ActualResult/login_wrong_username.png")

    def test_both_wrong(self, driver):
        login_page = LoginPage(driver)
        login_page.open_page()
        login_page.login("khong_ton_tai", "SaiMatKhau99")
        time.sleep(2)

        login_links = driver.find_elements(*LOGIN_LINK)
        assert len(login_links) > 0

        driver.save_screenshot("ActualResult/login_both_wrong.png")

@pytest.mark.selenium
class TestLoginValidation:
    def test_empty_username_prevents_submit(self, driver):
        login_page = LoginPage(driver)
        login_page.open_page()
        time.sleep(1)
        login_page.fill_field("pwd", "123456")
        login_page.submit()
        time.sleep(0.5)

        assert driver.current_url == LOGIN_URL
        driver.save_screenshot("ActualResult/login_empty_username.png")

    def test_empty_password_prevents_submit(self, driver):
        login_page = LoginPage(driver)
        login_page.open_page()
        time.sleep(1)
        login_page.fill_field("username", "ngocson")
        login_page.submit()
        time.sleep(0.5)

        assert driver.current_url == LOGIN_URL
        driver.save_screenshot("ActualResult/login_empty_password.png")

    def test_both_fields_empty_prevents_submit(self, driver):
        login_page = LoginPage(driver)
        login_page.open_page()
        time.sleep(1)
        login_page.submit()
        time.sleep(0.5)

        assert driver.current_url == LOGIN_URL
        driver.save_screenshot("ActualResult/login_both_empty.png")
