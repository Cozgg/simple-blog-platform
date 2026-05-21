# Simple Blog Platform

Python Flask MySQL Selenium Cloudinary

## Tóm tắt kết quả kiểm thử
| Số lượng unit test | Số lượng testcase | Tỉ lệ bao phủ mã nguồn (dao) |
|-------------------|-------------------|-----------------------------|
| 60/60 (Unit + API) | 25/25 (Selenium UI) | 86% |

## Giới thiệu
Simple Blog Platform là ứng dụng web được phát triển bằng Flask, giúp quản lý và đăng tải bài viết, với tính năng xác thực người dùng, quản lý bài viết, và tích hợp Cloudinary để lưu trữ hình ảnh.

## Tính năng
- Đăng nhập/Đăng ký bảo mật
- Đăng bài viết với hình ảnh
- Quản lý bài viết (thêm, sửa, xóa, khóa/mở khóa)
- Phân quyền người dùng (Admin, User)
- Theo dõi trạng thái bài viết
- Tích hợp Cloudinary để lưu trữ hình ảnh
- Giao diện responsive với Bootstrap

## Yêu cầu hệ thống
- Python 3.12 trở lên
- MySQL 8.0 trở lên
- Chrome/Edge browser (cho Selenium tests)
- Cloudinary account (để upload ảnh)

## Cài đặt

### 1. Tạo cơ sở dữ liệu
```sql
CREATE DATABASE blogdb;
```

### 2. Cấu hình kết nối MySQL
Mở tệp `blogapp/__init__.py` và thay đổi thông tin kết nối:

```python
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:password@localhost/blogdb?charset=utf8mb4"
```

### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 4. Cấu hình Cloudinary
Cloudinary đã được cấu hình sẵn trong `blogapp/__init__.py`. Nếu cần thay đổi, mở tệp và cập nhật:

```python
cloudinary.config(cloud_name='your_cloud_name',
                  api_key='your_api_key',
                  api_secret='your_api_secret')
```

## Chạy ứng dụng

### Cách 1: Sử dụng Flask
```bash
python -m blogapp.index
```

### Cách 2: Sử dụng flask run
```bash
flask run
```

## Đăng nhập mặc định
- Tên đăng nhập: admin
- Mật khẩu: 123456

## Kiểm thử

### Chạy kiểm thử
Chạy toàn bộ bộ kiểm thử:

```bash
pytest blogapp/test/ -v
```

Chạy một bộ kiểm thử cụ thể:

```bash
pytest blogapp/test/test_sel_create_post.py::test_tc1_create_post_success -v
```

Chạy kiểm thử với coverage:

```bash
pytest blogapp/test/ --cov=blogapp --cov-report=html
```

**Lưu ý quan trọng cho Selenium tests:**
- Flask app phải đang chạy trước khi chạy Selenium tests
- Mở terminal khác và chạy: `python -m blogapp.index` hoặc `flask run`
- Sau đó chạy Selenium tests ở terminal khác

### Cấu trúc kiểm thử
Dự án sử dụng pytest và Selenium để thực hiện các bài kiểm thử UI và kiểm thử đơn vị. Các bài kiểm thử được tổ chức theo cấu trúc sau:

- `blogapp/test/`: Chứa các lớp kiểm thử
- `blogapp/test/pages/`: Page Object Pattern cho Selenium (BasePage, HomePage, LoginPage, PostDetailPage, ProfilePage, RegisterPage, UserPostPage)
- `blogapp/test/test_base.py`: Cấu hình cơ sở cho Selenium WebDriver
- `blogapp/test/base.py`: Base test configuration

### Cấu hình kiểm thử
- Các kiểm thử sử dụng `conftest.py` để khởi tạo WebDriver
- Trước mỗi kiểm thử, user được đăng nhập vào hệ thống
- Sau mỗi kiểm thử, dữ liệu test được cleanup từ database

### Các loại kiểm thử

#### Selenium UI Tests
- `test_sel_create_post.py`: Kiểm thử UI tạo bài viết
  - TC1: Đăng bài thành công
  - TC2: Tiêu đề quá ngắn
  - TC3: Nội dung quá ngắn
  - TC4: Cả title và content đều sai
  - TC5: Cả hai trường trống
  - TC6: Tiêu đề trùng lặp trong ngày
  - TC7: Giới hạn 10 bài/ngày
  - TC8: Đăng bài có hình ảnh

- `test_sel_delete_comment.py`: Kiểm thử UI xóa bình luận
  - test_modal_delete_comment: Hiển thị modal xóa bình luận
  - test_modal_delete_reply_comment: Hiển thị modal xóa bình luận phản hồi
  - test_owner_click_delete_shows_modal: Owner click hiển thị modal xóa
  - test_1_owner_confirm_delete: Owner xác nhận xóa bình luận
  - test_2_owner_cancel_delete: Owner hủy xóa bình luận
  - test_tc3_owner_click_delete_shows_modal: TC3 owner click hiển thị modal
  - test_tc3_1_owner_confirm_delete: TC3 owner xác nhận xóa
  - test_tc3_2_owner_cancel_delete: TC3 owner hủy xóa
  - test_tc3_3_owner_close_delete_modal: TC3 owner đóng modal

- `test_sel_profile.py`: Kiểm thử UI profile
  - test_view_other_user_profile: Xem profile người khác
  - test_view_other_user_posts: Xem bài viết người khác
  - test_view_own_profile: Xem profile của chính mình

- `test_sel_login.py`: Kiểm thử UI đăng nhập
  - test_login_success: Đăng nhập thành công
  - test_login_fail_username: Sai tên đăng nhập
  - test_login_fail_password: Sai mật khẩu

- `test_sel_register.py`: Kiểm thử UI đăng ký
  - test_register_success: Đăng ký thành công
  - test_register_fail_username_exists: Tên đăng nhập đã tồn tại
  - test_register_fail_password_mismatch: Mật khẩu không khớp

- `test_sel_add_comment.py`: Kiểm thử UI thêm bình luận
  - test_add_comment_success: Thêm bình luận thành công
  - test_add_comment_fail_too_short: Bình luận quá ngắn
  - test_add_comment_fail_spam: Chống spam bình luận

- `test_sel_delete_post.py`: Kiểm thử UI xóa bài viết
  - test_delete_post_success: Xóa bài viết thành công
  - test_delete_post_with_confirm: Xóa bài viết có xác nhận
  - test_delete_pinned_post: Không xóa bài viết ghim

- `test_sel_pin_lock_post.py`: Kiểm thử UI ghim/khóa bài viết
  - test_pin_post_success: Ghim bài viết thành công
  - test_unpin_post_success: Bỏ ghim bài viết
  - test_lock_post_success: Khóa bài viết thành công
  - test_unlock_post_success: Mở khóa bài viết

#### Unit Tests - Comment Functionality
- `test_add_comment.py`: Kiểm thử DAO thêm bình luận
  - test_save_comment_success: Đăng bình luận thành công
  - test_save_comment_fail_permission: Giới hạn bình luận cho bài viết
  - test_save_comment_fail_locked_or_null_post: Bình luận vào bài bị khóa hoặc không tồn tại
  - test_save_comment_fail_anti_spam: Chống spam bình luận (không đăng liên tục)
  - test_save_comment_pass_after_wait: Đăng bình luận sau khi đợi đủ thời gian

- `test_delete_comment.py`: Kiểm thử DAO xóa bình luận
  - test_has_child_comments: Kiểm tra bình luận có phản hồi
  - test_get_all_child_ids: Lấy tất cả ID phản hồi con
  - test_delete_comment_by_comment_owner: Xóa bình luận bởi chủ bình luận
  - test_delete_comment_by_post_owner: Xóa bình luận bởi chủ bài viết
  - test_delete_comment_no_permission: Không có quyền xóa bình luận
  - test_delete_non_existent_comment: Xóa bình luận không tồn tại

#### Unit Tests - Post Functionality
- `test_post.py`: Kiểm thử DAO bài viết
  - test_existing_post: Kiểm tra bài viết tồn tại
  - test_not_existing_post: Kiểm tra bài viết không tồn tại
  - test_post_limit: Giới hạn số bài viết và trùng lặp tiêu đề
  - test_add_post_with_image: Thêm bài viết có hình ảnh (mock Cloudinary)
  - test_add_post_exception: Xử lý exception khi thêm bài viết
  - test_delete_pinned_post: Không xóa bài viết đang ghim
  - test_delete_over_10_comments: Cần xác nhận khi xóa bài có >10 bình luận
  - test_delete_over_10_comments_confirmed: Xóa bài có >10 bình luận khi đã xác nhận
  - test_delete_wrong_permission: Không có quyền xóa bài viết
  - test_delete_post_all: Kiểm thử xóa bài viết với nhiều trường hợp (parameterized)
  - test_count_posts: Đếm số bài viết

- `test_search_posts.py`: Kiểm thử tìm kiếm bài viết
  - test_keyword: Tìm kiếm theo từ khóa
  - test_pagination: Phân trang bài viết

#### Unit Tests - User Functionality
- `test_get_user.py`: Kiểm thử lấy thông tin user
  - test_get_user_detail: Lấy chi tiết user theo ID
  - test_get_all_users: Lấy danh sách tất cả users

#### API Tests
- `test_api_post.py`: Kiểm thử API tạo bài viết
  - test_create_post_success: Tạo bài viết thành công
  - test_create_post_invalid_title: Tiêu đề không hợp lệ
  - test_create_post_invalid_content: Nội dung không hợp lệ
  - test_create_post_not_logged_in: Chưa đăng nhập

- `test_api_add_comment.py`: Kiểm thử API thêm bình luận
  - test_comment_success: Thêm bình luận thành công
  - test_prevent_comment_spam: Chống spam bình luận
  - test_prevent_comment_not_enough_character: Bình luận quá ngắn
  - test_prevent_comment_post_locked_or_null_post: Bình luận vào bài bị khóa hoặc không tồn tại
  - test_reached_comment_limit: Đạt giới hạn bình luận
  - test_comment_system_error: Lỗi hệ thống khi thêm bình luận

- `test_api_delete_comment.py`: Kiểm thử API xóa bình luận
  - test_delete_comment_api_success: Xóa bình luận thành công
  - test_delete_comment_api_errors: Các lỗi khi xóa bình luận (parameterized)

- `test_api_delete_post.py`: Kiểm thử API xóa bài viết
  - test_delete_post_success_no_comment: Xóa bài viết không có bình luận
  - test_delete_post_success_with_confirmed: Xóa bài viết có xác nhận
  - test_delete_post_error: Các lỗi khi xóa bài viết (parameterized)

- `test_api_pin_lock_post.py`: Kiểm thử API ghim/khóa bài viết
  - test_pin_post_success: Ghim bài viết thành công
  - test_unpin_post_success: Bỏ ghim bài viết
  - test_lock_post_success: Khóa bài viết thành công
  - test_unlock_post_success: Mở khóa bài viết
  - test_pin_post_error: Các lỗi khi ghim bài viết (parameterized)
  - test_lock_post_error: Các lỗi khi khóa bài viết (parameterized)

### Phương pháp kiểm thử
- **Selenium Test**: Kiểm thử UI với Page Object Pattern
- **Unit Test**: Kiểm thử đơn vị cơ bản với pytest
- **Integration Test**: Kiểm thử tích hợp với database và Cloudinary

### Ví dụ kiểm thử

#### Kiểm thử UI cơ bản:
```python
def test_tc1_create_post_success(driver):
    login_page = LoginPage(driver)
    login_page.open_page()
    login_page.login("ngocson", "123456")

    home_page = HomePage(driver)
    home_page.open()
    home_page.open_create_modal()

    test_title = f"Tiêu đề bài viết {int(time.time())}"
    valid_content = "Nội dung bài viết hợp lệ dài trên 50 ký tự để được đăng okeokeokeokeokeokeokeoke."

    home_page.submit_post_ui(test_title, valid_content)
    home_page.wait_for_success_and_refresh(test_title)
    assert test_title in driver.page_source
```

#### Kiểm thử DAO:
```python
def test_save_comment_success(sample_data, test_session):
    user_id = sample_data[10].id
    post_id = sample_data[0].id
    content = "Đây là bình luận hợp lệ"

    dao.save_comment(content, post_id, user_id)
    saved_comment = Comment.query.filter_by(content=content, user_id=user_id).first()
    assert saved_comment is not None
    assert saved_comment.post_id == post_id
```

#### Kiểm thử UI validation:
```python
def test_tc2_create_post_fail_title_too_short(driver):
    login_page = LoginPage(driver)
    login_page.open_page()
    login_page.login("ngocson", "123456")

    home_page = HomePage(driver)
    home_page.open()
    home_page.open_create_modal()
    home_page.submit_post_ui("Ngắn", "Nội dung đủ dài để đăng bài viết okeokeokeokeokeoke")

    home_page.wait_for_inline_error()
    errors = home_page.get_inline_errors()

    assert 'title' in errors
    assert "Tiêu đề phải từ 10 đến 200 ký tự" in errors['title']
```

#### Kiểm thử API:
```python
def test_create_post_success(test_client, mocker):
    mock_login(mocker)
    add_post_mock = mocker.patch("blogapp.dao.add_post", return_value=(True, "Đăng bài viết thành công"))

    res = test_client.post(
        "/api/posts",
        data={
            "title": "Tiêu đề bài viết hợp lệ dài trên 10 ký tự",
            "content": "Nội dung bài viết hợp lệ dài trên 50 ký tự..."
        }
    )

    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == 200
    assert data["msg"] == "Đăng bài viết thành công"
    add_post_mock.assert_called_once()
```

### Viết kiểm thử mới
1. Tạo lớp kiểm thử trong `blogapp/test/`
2. Sử dụng `driver` fixture từ `conftest.py` cho Selenium tests
3. Sử dụng Page Object Pattern từ `blogapp/test/pages/`
4. Viết các phương thức kiểm thử với annotation `@pytest.fixture`
5. Sử dụng các phương thức assert để kiểm tra kết quả
6. Cleanup dữ liệu test sau khi hoàn thành

## Cấu trúc dự án
```
simple-blog-platform/
├── blogapp/
│   ├── __init__.py          # Cấu hình Flask và database
│   ├── admin.py             # Flask-Admin configuration
│   ├── dao.py               # Data Access Object
│   ├── decorators.py        # Custom decorators
│   ├── index.py             # Main routes and controllers
│   ├── models.py            # SQLAlchemy models
│   ├── utils.py             # Utility functions
│   ├── static/              # Static files (CSS, JS, images)
│   ├── templates/           # HTML templates
│   └── test/                # Test directory
│       ├── pages/           # Page Object Pattern
│       │   ├── BasePage.py
│       │   ├── HomePage.py
│       │   ├── LoginPage.py
│       │   ├── PostDetailPage.py
│       │   ├── ProfilePage.py
│       │   ├── RegisterPage.py
│       │   └── UserPostPage.py
│       ├── base.py          # Base test configuration
│       ├── test_base.py     # Selenium WebDriver configuration
│       ├── test_sel_create_post.py     # Selenium tests for creating posts
│       ├── test_sel_delete_comment.py   # Selenium tests for deleting comments
│       ├── test_sel_profile.py          # Selenium tests for profile pages
│       ├── test_sel_login.py            # Selenium tests for login
│       ├── test_sel_register.py         # Selenium tests for registration
│       ├── test_sel_add_comment.py      # Selenium tests for adding comments
│       ├── test_sel_delete_post.py      # Selenium tests for deleting posts
│       ├── test_sel_pin_lock_post.py    # Selenium tests for pinning/locking posts
│       ├── test_add_comment.py           # Unit tests for adding comments
│       ├── test_delete_comment.py       # Unit tests for deleting comments
│       ├── test_post.py                 # Unit tests for posts
│       ├── test_search_posts.py         # Unit tests for searching posts
│       ├── test_get_user.py             # Unit tests for user info
│       ├── test_api_post.py             # API tests for posts
│       ├── test_api_add_comment.py      # API tests for adding comments
│       ├── test_api_delete_comment.py   # API tests for deleting comments
│       ├── test_api_delete_post.py      # API tests for deleting posts
│       └── test_api_pin_lock_post.py    # API tests for pinning/locking posts
├── requirements.txt        # Python dependencies
├── pytest.ini             # Pytest configuration
├── .env                    # Environment variables
└── README.md              # Project documentation
```

## Công nghệ sử dụng
- **Flask**: Web framework
- **SQLAlchemy**: ORM
- **MySQL**: Cơ sở dữ liệu
- **Flask-Login**: Authentication
- **Flask-Mail**: Email services
- **Cloudinary**: Image storage
- **Selenium**: UI testing
- **pytest**: Testing framework
- **Bootstrap**: UI framework
- **jQuery**: JavaScript library

## Bản quyền
Phần mềm được phát triển dưới giấy phép MIT License.
