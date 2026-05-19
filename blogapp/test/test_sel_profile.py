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


@pytest.fixture
def seed_other_user(test_app):
    with test_app.app_context():
        def hash_pass(password):
            return str(hashlib.md5(password.encode('utf-8')).hexdigest())
        ngocson = User.query.filter_by(username='ngocson').first()
        if not ngocson:
            ngocson = User(
                name='Ngọc Sơn',
                username='ngocson',
                password=hash_pass("123456"),
                email="ngocson@gmail.com"
            )
            db.session.add(ngocson)
            db.session.commit()
        
        other_user = User(
            name='Người dùng khác',
            username='otheruser',
            password=hash_pass("123456"),
            email="otheruser@gmail.com"
        )
        db.session.add(other_user)
        db.session.commit()
        post = Post(
            title="Bài viết của người dùng khác",
            content="Đây là nội dung bài viết của người dùng khác để test tính năng xem trang cá nhân.",
            user_id=other_user.id
        )
        db.session.add(post)
        db.session.commit()
        
        yield other_user.id
        
        db.session.delete(post)
        db.session.delete(other_user)
        db.session.commit()


@pytest.fixture
def seed_user_with_many_posts(test_app):
    with test_app.app_context():
        def hash_pass(password):
            return str(hashlib.md5(password.encode('utf-8')).hexdigest())
        
        user = User.query.filter_by(username='ngocson').first()
        if not user:
            user = User(
                name='Ngọc Sơn',
                username='ngocson',
                password=hash_pass("123456"),
                email="ngocson@gmail.com"
            )
            db.session.add(user)
            db.session.commit()
        
        # Create 5 posts (more than PAGE_SIZE=2)
        posts = []
        for i in range(1, 6):
            post = Post(
                title=f"Bài viết số {i}",
                content=f"Đây là nội dung bài viết số {i} để test pagination.",
                user_id=user.id
            )
            posts.append(post)
            db.session.add(post)
        db.session.commit()
        
        yield user.id
        
        for post in posts:
            db.session.delete(post)
        db.session.commit()


@pytest.mark.selenium
def test_view_other_user_profile(driver):
    login_page = LoginPage(driver)
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
    
    driver.save_screenshot('test_view_other_profile.png')


@pytest.mark.selenium
def test_view_other_user_posts(driver):
    login_page = LoginPage(driver)
    login_page.login("ngocson", "123456")
    t.sleep(2)
    
    profile_page = ProfilePage(driver)
    profile_page.open_page(3)
    t.sleep(2)
    
    post_titles = profile_page.get_post_titles()
    assert len(post_titles) > 0, "Phải có ít nhất một bài đăng"
    
    driver.save_screenshot('test_view_other_user_posts.png')


@pytest.mark.selenium
def test_profile_pagination(driver):
    login_page = LoginPage(driver)
    login_page.login("ngocson", "123456")
    t.sleep(2)
    
    profile_page = ProfilePage(driver)
    profile_page.open_page(2)
    t.sleep(2)
    
    has_pagination = profile_page.has_pagination()
    print(f"Pagination present: {has_pagination}")
    
    if has_pagination:
        initial_posts = profile_page.get_post_titles()
        print(f"Initial posts count: {len(initial_posts)}")
        
        profile_page.click_next_page()
        t.sleep(2)
        
        next_page_posts = profile_page.get_post_titles()
        print(f"Next page posts count: {len(next_page_posts)}")
        
        assert initial_posts != next_page_posts, "Bài đăng phải khác nhau trong các trang"
        
        profile_page.click_prev_page()
        t.sleep(2)
        
        back_posts = profile_page.get_post_titles()
        assert initial_posts == back_posts, "Phải quay lại trang 1"
    
    driver.save_screenshot('test_profile_pagination.png')


@pytest.mark.selenium
def test_view_own_profile(driver):
    login_page = LoginPage(driver)
    login_page.login("ngocson", "123456")
    
    profile_page = ProfilePage(driver)
    profile_page.open_page(2)
    
    user_name = profile_page.get_user_name()
    assert "Ngọc Sơn" in user_name
    
    user_info = profile_page.get_user_info()
    assert "@ngocson" in user_info
    
    driver.save_screenshot('test_view_own_profile.png')
