import pytest
import os
import hashlib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from blogapp import app, db
from blogapp.models import User, UserRole, Post

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    def hash_pass(password):
        return str(hashlib.md5(password.encode('utf-8')).hexdigest())

    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            default_avt = "https://res.cloudinary.com/dpl8syyb9/image/upload/v1764237405/ecjxy41wdhl7k03scea8.jpg"
            admin_user = User(
                name='Quản trị viên',
                username='admin',
                password=hash_pass("admin123"),
                user_role=UserRole.ADMIN,
                email="admin@blog.com",
                avatar=default_avt
            )
            db.session.add(admin_user)
            
            users = [
                User(name='Ngọc Sơn', username='ngocson',
                     password=hash_pass("123456"), user_role=UserRole.USER,
                     email="ngocson@gmail.com", avatar=default_avt),
            ]
            db.session.add_all(users)
            db.session.commit()
    yield

@pytest.fixture
def driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    # For CI environment (Ubuntu with Chromium)
    if os.getenv('CHROME_DRIVER_PATH'):
        from selenium.webdriver.chrome.service import Service
        service = Service(os.getenv('CHROME_DRIVER_PATH'))
        chrome_options.binary_location = '/usr/bin/chromium-browser'
        _driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        _driver = webdriver.Chrome(options=chrome_options)

    yield _driver
    _driver.quit()
