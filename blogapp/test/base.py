import pytest
import os
from datetime import datetime
from flask import Flask
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

from blogapp import db, login
from blogapp.index import register_routers
from blogapp.models import User, Post, UserRole


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["PAGE_SIZE"] = 2
    app.config['TESTING'] = True
    app.secret_key = 'afhfejsdfsdfHJBhj7'
    db.init_app(app)
    login.init_app(app)

    register_routers(app=app)

    return app


@pytest.fixture
def test_app():
    app = create_app()
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def test_client(test_app):
    return test_app.test_client()


@pytest.fixture
def test_session(test_app):
    yield db.session
    db.session.rollback()

@pytest.fixture(scope="session")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--remote-debugging-port=9222')
    options.binary_location = '/usr/bin/chromium-browser'
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


@pytest.fixture(scope="session", autouse=True)
def setup_selenium_db():
    """Setup database with test data for Selenium tests"""
    from blogapp import app
    with app.app_context():
        # Create users
        user1 = User.query.filter_by(username='ngocson').first()
        if not user1:
            user1 = User(name='Ngọc Sơn', username='ngocson',
                        password='e10adc3949ba59abbe56e057f20f883e',
                        email='ngocson@example.com', user_role=UserRole.USER)
            db.session.add(user1)

        user2 = User.query.filter_by(username='canhhuynh').first()
        if not user2:
            user2 = User(name='Canh Huỳnh', username='canhhuynh',
                        password='e10adc3949ba59abbe56e057f20f883e',
                        email='canhhuynh@example.com', user_role=UserRole.USER)
            db.session.add(user2)

        db.session.commit()

        # Create test posts for comment tests
        post1 = Post.query.filter_by(id=1).first()
        if not post1:
            post1 = Post(title='Bài viết test 1', content='Nội dung bài viết test 1 dài trên 50 ký tự để được đăng thành công.',
                        user_id=user1.id, created_date=datetime.now())
            db.session.add(post1)

        post3 = Post.query.filter_by(id=3).first()
        if not post3:
            post3 = Post(title='Bài viết test 3', content='Nội dung bài viết test 3 dài trên 50 ký tự để được đăng thành công.',
                        user_id=user1.id, created_date=datetime.now())
            db.session.add(post3)

        db.session.commit()
        yield
        # Cleanup test posts after all tests
        test_posts = Post.query.filter(Post.title.like('%test%')).all()
        for post in test_posts:
            db.session.delete(post)
        db.session.commit()