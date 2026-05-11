import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from blogapp import app, db
from blogapp.models import Post

from blogapp.test.pages.CreatePostPage import CreatePostPage

class TestCreatePost(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.base_url = "http://127.0.0.1:5000"
        
        self.driver.get(f"{self.base_url}/login")
        self.driver.find_element(By.NAME, "username").send_keys("admin")
        self.driver.find_element(By.NAME, "password").send_keys("admin123")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        time.sleep(2) 
        self.create_post_page = CreatePostPage(self.driver)
        self.create_post_page.navigate(self.base_url)

    def tearDown(self):
        self.driver.quit()
        
        if hasattr(self, 'test_title'):
            with app.app_context():
                post_to_delete = Post.query.filter_by(title=self.test_title).first()
                if post_to_delete:
                    db.session.delete(post_to_delete)
                    db.session.commit()

    def test_tc1_create_post_success(self):
        self.test_title = f"Tiêu đề bài viết {int(time.time())}"
        valid_content = "Nội dung bài viết hợp lệ dài trên 50 ký tự để vượt qua bước kiểm tra."
        
        self.create_post_page.create_post(self.test_title, valid_content)
        
        time.sleep(2)
        self.assertEqual(self.driver.current_url, f"{self.base_url}/")

    def test_tc2_create_post_fail_title_too_short(self):
        self.test_title = f"Ngắn {int(time.time())}"
        
        self.create_post_page.create_post("Ngắn", "Nội dung hợp lệ dài trên 50 ký tự...")
        
        title_element = self.create_post_page.find(*self.create_post_page.TITLE_INPUT)
        msg = self.driver.execute_script("return arguments[0].validationMessage;", title_element)
        self.assertTrue(len(msg) > 0)