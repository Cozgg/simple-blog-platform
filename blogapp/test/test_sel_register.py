import os
import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from blogapp.test.test_base import driver
from blogapp.test.pages.LoginPage import LoginPage
from blogapp.test.pages.RegisterPage import RegisterPage

BASE_URL = "http://127.0.0.1:5000"
REGISTER_URL = f"{BASE_URL}/register"
LOGIN_URL = f"{BASE_URL}/login"

AVATAR_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'static', 'img', 'lucasimg.jpg')
)


def unique_username():
    return f"user{int(time.time() * 1000)}"


def unique_email():
    return f"test{int(time.time() * 1000)}@gmail.com"

@pytest.mark.selenium
class TestRegisterSuccess:
    def test_register_success(self, driver):
        if not os.path.exists(AVATAR_PATH):
            pytest.skip("Khong tim thay file anh test")

        reg_page = RegisterPage(driver)
        reg_page.open_page()
        username = unique_username()
        reg_page.register(
            name="Nguoi Dung Test",
            username=username,
            email=unique_email(),
            password="Test1234",
            confirm="Test1234",
            avatar_path=AVATAR_PATH,
        )

        try:
            WebDriverWait(driver, 15).until(EC.url_contains("/login"))
        except Exception:
            driver.save_screenshot("ActualResult/register_success.png")
            pytest.fail(f"Van o /register. Loi: {reg_page.get_error_message()}")

        driver.save_screenshot("ActualResult/register_success.png")
        assert "/login" in driver.current_url

    def test_register_success_then_login(self, driver):
        if not os.path.exists(AVATAR_PATH):
            pytest.skip("Khong tim thay file anh test")

        reg_page = RegisterPage(driver)
        reg_page.open_page()
        username = unique_username()
        reg_page.register(
            name="Nguoi Dung Test",
            username=username,
            email=unique_email(),
            password="Test1234",
            confirm="Test1234",
            avatar_path=AVATAR_PATH,
        )

        try:
            WebDriverWait(driver, 15).until(EC.url_contains("/login"))
        except Exception:
            driver.save_screenshot("ActualResult/register_then_login.png")
            pytest.fail(f"Dang ky that bai: {reg_page.get_error_message()}")

        login_page = LoginPage(driver)
        login_page.open_page()
        login_page.login(username, "Test1234")
        time.sleep(2)

        assert driver.current_url == f"{BASE_URL}/"
        assert driver.find_elements(By.CSS_SELECTOR, "a[href='/logout']")
        driver.save_screenshot("ActualResult/register_then_login.png")

@pytest.mark.selenium
class TestRegisterServerValidation:

    def test_password_mismatch(self, driver):
        reg_page = RegisterPage(driver)
        reg_page.open_page()
        reg_page.bypass_all_required()
        reg_page.register(
            name="Test User", username=unique_username(), email=unique_email(),
            password="Test1234", confirm="KhacNhau99",
        )
        time.sleep(1)
        assert reg_page.get_error_message() is not None
        driver.save_screenshot("ActualResult/register_password_mismatch.png")

    def test_username_too_short(self, driver):
        reg_page = RegisterPage(driver)
        reg_page.open_page()
        reg_page.bypass_all_required()
        reg_page.register(
            name="Test User", username="abc", email=unique_email(),
            password="Test1234", confirm="Test1234",
        )
        time.sleep(1)
        assert reg_page.get_error_message() is not None
        driver.save_screenshot("ActualResult/register_username_too_short.png")

    def test_password_too_short(self, driver):
        reg_page = RegisterPage(driver)
        reg_page.open_page()
        reg_page.bypass_all_required()
        reg_page.register(
            name="Test User", username=unique_username(), email=unique_email(),
            password="Ab1", confirm="Ab1",
        )
        time.sleep(1)
        assert reg_page.get_error_message() is not None
        driver.save_screenshot("ActualResult/register_password_too_short.png")

    def test_password_no_digit(self, driver):
        reg_page = RegisterPage(driver)
        reg_page.open_page()
        reg_page.bypass_all_required()
        reg_page.register(
            name="Test User", username=unique_username(), email=unique_email(),
            password="TestPass", confirm="TestPass",
        )
        time.sleep(1)
        assert reg_page.get_error_message() is not None
        driver.save_screenshot("ActualResult/register_password_no_digit.png")

    def test_password_no_lowercase(self, driver):
        reg_page = RegisterPage(driver)
        reg_page.open_page()
        reg_page.bypass_all_required()
        reg_page.register(
            name="Test User", username=unique_username(), email=unique_email(),
            password="TESTPASS1", confirm="TESTPASS1",
        )
        time.sleep(1)
        assert reg_page.get_error_message() is not None
        driver.save_screenshot("ActualResult/register_password_no_lowercase.png")

    def test_password_no_uppercase(self, driver):
        reg_page = RegisterPage(driver)
        reg_page.open_page()
        reg_page.bypass_all_required()
        reg_page.register(
            name="Test User", username=unique_username(), email=unique_email(),
            password="testpass1", confirm="testpass1",
        )
        time.sleep(1)
        assert reg_page.get_error_message() is not None
        driver.save_screenshot("ActualResult/register_password_no_uppercase.png")

    def test_duplicate_username(self, driver):
        reg_page = RegisterPage(driver)
        reg_page.open_page()
        reg_page.bypass_all_required()
        reg_page.register(
            name="Test User", username="ngocson", email=unique_email(),
            password="Test1234", confirm="Test1234",
        )
        time.sleep(1)
        assert reg_page.get_error_message() is not None
        driver.save_screenshot("ActualResult/register_duplicate_username.png")

@pytest.mark.selenium
class TestRegisterClientValidation:

    def test_empty_name_prevents_submit(self, driver):
        reg_page = RegisterPage(driver)
        reg_page.open_page()
        time.sleep(1)
        reg_page.fill_field("username", "testuser99")
        reg_page.fill_field("email", "test@gmail.com")
        reg_page.fill_field("pwd", "Test1234")
        reg_page.fill_field("confirm", "Test1234")
        reg_page.submit()
        time.sleep(0.5)
        assert driver.current_url == REGISTER_URL
        driver.save_screenshot("ActualResult/register_empty_name.png")

    def test_empty_username_prevents_submit(self, driver):
        reg_page = RegisterPage(driver)
        reg_page.open_page()
        time.sleep(1)
        reg_page.fill_field("name", "Test User")
        reg_page.fill_field("email", "test@gmail.com")
        reg_page.fill_field("pwd", "Test1234")
        reg_page.fill_field("confirm", "Test1234")
        reg_page.submit()
        time.sleep(0.5)
        assert driver.current_url == REGISTER_URL
        driver.save_screenshot("ActualResult/register_empty_username.png")

    def test_empty_email_prevents_submit(self, driver):
        reg_page = RegisterPage(driver)
        reg_page.open_page()
        time.sleep(1)
        reg_page.fill_field("name", "Test User")
        reg_page.fill_field("username", "testuser99")
        reg_page.fill_field("pwd", "Test1234")
        reg_page.fill_field("confirm", "Test1234")
        reg_page.submit()
        time.sleep(0.5)
        assert driver.current_url == REGISTER_URL
        driver.save_screenshot("ActualResult/register_empty_email.png")

    def test_empty_password_prevents_submit(self, driver):
        reg_page = RegisterPage(driver)
        reg_page.open_page()
        time.sleep(1)
        reg_page.fill_field("name", "Test User")
        reg_page.fill_field("username", "testuser99")
        reg_page.fill_field("email", "test@gmail.com")
        reg_page.fill_field("confirm", "Test1234")
        reg_page.submit()
        time.sleep(0.5)
        assert driver.current_url == REGISTER_URL
        driver.save_screenshot("ActualResult/register_empty_password.png")

    def test_empty_confirm_prevents_submit(self, driver):
        reg_page = RegisterPage(driver)
        reg_page.open_page()
        time.sleep(1)
        reg_page.fill_field("name", "Test User")
        reg_page.fill_field("username", "testuser99")
        reg_page.fill_field("email", "test@gmail.com")
        reg_page.fill_field("pwd", "Test1234")
        reg_page.submit()
        time.sleep(0.5)
        assert driver.current_url == REGISTER_URL
        driver.save_screenshot("ActualResult/register_empty_confirm.png")

    def test_all_fields_empty_prevents_submit(self, driver):
        reg_page = RegisterPage(driver)
        reg_page.open_page()
        time.sleep(1)
        reg_page.submit()
        time.sleep(0.5)
        assert driver.current_url == REGISTER_URL
        driver.save_screenshot("ActualResult/register_all_empty.png")
