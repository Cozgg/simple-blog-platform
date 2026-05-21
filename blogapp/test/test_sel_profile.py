import pytest
from blogapp.test.pages.LoginPage import LoginPage
from blogapp.test.pages.HomePage import HomePage
from blogapp.test.pages.ProfilePage import ProfilePage
from blogapp.test.base import driver, test_app
from blogapp import db
from blogapp.models import User, Post
from datetime import datetime
import hashlib
import time as t


@pytest.mark.selenium
def test_view_other_user_profile(driver):
    login_page = LoginPage(driver)
    login_page.open_page()
    login_page.login("ngocson", "123456")
    t.sleep(2)
    
    profile_page = ProfilePage(driver)
    profile_page.open_page(3) 
    t.sleep(2)
    
    print(f"Current URL: {driver.current_url}")
    user_name = profile_page.get_user_name()
    print(f"User name found: {user_name}")
    
    assert "Thế Cảnh" in user_name
    
    user_info = profile_page.get_user_info()
    assert "@canhhuynh" in user_info
    


@pytest.mark.selenium
def test_view_other_user_posts(driver):
    login_page = LoginPage(driver)
    login_page.open_page()
    login_page.login("ngocson", "123456")
    t.sleep(2)
    
    profile_page = ProfilePage(driver)
    profile_page.open_page(3) 
    t.sleep(2)
    
    post_titles = profile_page.get_post_titles()
    assert len(post_titles) > 0, "Phải có ít nhất một bài đăng"
    profile_page.click_post_detail(index=0)
    t.sleep(2)
    


@pytest.mark.selenium
def test_view_own_profile(driver):
    login_page = LoginPage(driver)
    login_page.open_page()
    login_page.login("ngocson", "123456")
    t.sleep(2)
    
    profile_page = ProfilePage(driver)
    profile_page.open_page(2)
    t.sleep(2)
    
    user_name = profile_page.get_user_name()
    assert "Ngọc Sơn" in user_name
    
    user_info = profile_page.get_user_info()
    assert "@ngocson" in user_info
    
