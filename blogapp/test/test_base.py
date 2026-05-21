import pytest
import os
import hashlib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from blogapp import app, db
from blogapp.models import User, UserRole, Post, Comment


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

    if os.getenv('CHROME_DRIVER_PATH'):
        from selenium.webdriver.chrome.service import Service
        service = Service(os.getenv('CHROME_DRIVER_PATH'))
        chrome_options.binary_location = '/usr/bin/chromium-browser'
        _driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        _driver = webdriver.Chrome(options=chrome_options)

    yield _driver
    _driver.quit()

def create_post(
    title="Test Post Valid Title",
    user_id=1,
    comments_count=0,
    is_pinned=False,
    is_locked=False
):

    post = Post(
        title=title,
        content="Mock content",
        user_id=user_id,
        is_pinned=is_pinned,
        is_locked=is_locked
    )

    db.session.add(post)
    db.session.flush()

    comments = []

    for i in range(comments_count):
        c = Comment(
            content=f"Comment {i}",
            user_id=user_id,
            post_id=post.id
        )

        comments.append(c)

    db.session.add_all(comments)
    db.session.commit()

    return post

@pytest.fixture
def post_factory():

    created_posts = []

    def _create_post(
        username="admin",
        comments_count=0,
        is_pinned=False,
        is_locked=False
    ):

        with app.app_context():

            user = User.query.filter_by(
                username=username
            ).first()

            post = create_post(
                user_id=user.id,
                comments_count=comments_count,
                is_pinned=is_pinned,
                is_locked=is_locked
            )

            created_posts.append(post.id)

            return post

    yield _create_post

    with app.app_context():

        for post_id in created_posts:

            post = Post.query.get(post_id)

            if post:
                db.session.delete(post)

        db.session.commit()
