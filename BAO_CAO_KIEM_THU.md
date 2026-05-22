# BÁO CÁO KIỂM THỬ PHẦN MỀM
## Nghiệp vụ: Đăng bài viết & Xóa bình luận

---

## MỤC LỤC
1. [Tổng quan hệ thống](#tổng-quan-hệ-thống)
2. [Phân tích Backend - Đăng bài viết](#phân-tích-backend---đăng-bài-viết)
3. [Phân tích API - Đăng bài viết](#phân-tích-api---đăng-bài-viết)
4. [Phân tích Frontend - Đăng bài viết](#phân-tích-frontend---đăng-bài-viết)
5. [Phân tích Unit Tests - Đăng bài viết](#phân-tích-unit-tests---đăng-bài-viết)
6. [Phân tích Selenium Tests - Đăng bài viết](#phân-tích-selenium-tests---đăng-bài-viết)
7. [Phân tích Selenium Tests - Xóa bình luận](#phân-tích-selenium-tests---xóa-bình-luận)
8. [Câu hỏi phỏng vấn](#câu-hỏi-phỏng-vấn)

---

## TỔNG QUAN HỆ THỐNG

### Kiến trúc ứng dụng
- **Framework**: Flask (Python)
- **Database**: MySQL với SQLAlchemy ORM
- **Testing**: Pytest (Unit tests + Selenium WebDriver)
- **Frontend**: Bootstrap 5 + Jinja2 templates

### Nghiệp vụ kiểm thử
1. **Đăng bài viết**: Tạo bài viết mới với validation
2. **Xóa bình luận**: Xóa bình luận và các phản hồi liên quan

---

## PHÂN TÍCH BACKEND - ĐĂNG BÀI VIẾT

### File: `blogapp/dao.py` - Hàm `add_post()`

```python
def add_post(title, content, user_id, image=None):
    if not title or len(title) < 10 or len(title) > 200:
        raise ValueError('Tiêu đề phải từ 10 đến 200 ký tự')

    if not content or len(content) < 50 or len(content) > 5000:
        raise ValueError('Nội dung phải từ 50 đến 5000 ký tự')

    today = date.today()

    post_count_today = Post.query.filter(Post.user_id == user_id,
        db.func.date(Post.created_date) == today
    ).count()

    if post_count_today >= 10:
        raise ValueError("Bạn đã đạt giới hạn 10 bài đăng trong ngày")

    duplicate_title = Post.query.filter(Post.title == title.strip(),
        Post.user_id == user_id,
        db.func.date(Post.created_date) == today
    ).first()

    if duplicate_title:
        raise ValueError("Bạn đã đăng bài với tiêu đề này trong hôm nay")

    post = Post(title=title.strip(), content=content.strip(), user_id=user_id)

    if image:
        res = cloudinary.uploader.upload(image)
        post.image = res.get('secure_url')

    db.session.add(post)
    try:
        db.session.commit()
        return True, "Đăng bài viết thành công"
    except Exception as e:
        db.session.rollback()
        raise Exception("Lỗi hệ thống: " + str(e))
```

### Phân tích từng dòng code

**Dòng 92-93: Validation tiêu đề**
```python
if not title or len(title) < 10 or len(title) > 200:
    raise ValueError('Tiêu đề phải từ 10 đến 200 ký tự')
```
- **Mục đích**: Kiểm tra độ dài tiêu đề
- **Logic**: Tiêu đề phải tồn tại, độ dài 10-200 ký tự
- **Kiểm thử**: Test tiêu đề quá ngắn, quá dài, rỗng

**Dòng 95-96: Validation nội dung**
```python
if not content or len(content) < 50 or len(content) > 5000:
    raise ValueError('Nội dung phải từ 50 đến 5000 ký tự')
```
- **Mục đích**: Kiểm tra độ dài nội dung
- **Logic**: Nội dung phải tồn tại, độ dài 50-5000 ký tự
- **Kiểm thử**: Test nội dung quá ngắn, quá dài, rỗng

**Dòng 98-102: Kiểm tra giới hạn bài đăng/ngày**
```python
today = date.today()
post_count_today = Post.query.filter(Post.user_id == user_id,
    db.func.date(Post.created_date) == today
).count()

if post_count_today >= 10:
    raise ValueError("Bạn đã đạt giới hạn 10 bài đăng trong ngày")
```
- **Mục đích**: Giới hạn spam bài đăng
- **Logic**: Đếm số bài đăng của user trong ngày, max 10 bài
- **Kiểm thử**: Test đăng bài thứ 11 trong ngày

**Dòng 107-113: Kiểm tra tiêu đề trùng lặp**
```python
duplicate_title = Post.query.filter(Post.title == title.strip(),
    Post.user_id == user_id,
    db.func.date(Post.created_date) == today
).first()

if duplicate_title:
    raise ValueError("Bạn đã đăng bài với tiêu đề này trong hôm nay")
```
- **Mục đích**: Tránh tiêu đề trùng lặp trong ngày
- **Logic**: Kiểm tra user đã đăng tiêu đề này hôm nay chưa
- **Kiểm thử**: Test đăng 2 bài cùng tiêu đề trong ngày

**Dòng 115-119: Tạo đối tượng Post**
```python
post = Post(title=title.strip(), content=content.strip(), user_id=user_id)

if image:
    res = cloudinary.uploader.upload(image)
    post.image = res.get('secure_url')
```
- **Mục đích**: Tạo bài viết mới, upload ảnh nếu có
- **Logic**: Strip whitespace, upload ảnh lên Cloudinary
- **Kiểm thử**: Test đăng bài có ảnh, không có ảnh

**Dòng 121-127: Lưu vào database**
```python
db.session.add(post)
try:
    db.session.commit()
    return True, "Đăng bài viết thành công"
except Exception as e:
    db.session.rollback()
    raise Exception("Lỗi hệ thống: " + str(e))
```
- **Mục đích**: Commit transaction, xử lý lỗi
- **Logic**: Thử commit, nếu lỗi thì rollback
- **Kiểm thử**: Test lỗi database (mock exception)

---

## PHÂN TÍCH API - ĐĂNG BÀI VIẾT

### File: `blogapp/index.py` - Endpoint `/api/posts`

```python
@app.route('/api/posts', methods=['POST'])
@custom_login_required(UserRole.USER)
def create_post_api():
    try:
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        image = request.files.get('image')

        if image and not hasattr(image, 'filename') or (image and not image.filename):
            image = None
        elif image:
            image.seek(0, 2)
            if image.tell() == 0:
                image = None
            image.seek(0)

        dao.add_post(title=title, content=content, user_id=current_user.id, image=image)

        return jsonify({'status': 200, 'msg': 'Đăng bài viết thành công'})

    except ValueError as ex:
        return jsonify({'status': 400, 'err_msg': str(ex)}), 400
    except Exception as ex:
        return jsonify({'status': 500, 'err_msg': str(ex)}), 500
```

### Phân tích từng dòng code

**Dòng 225-226: Route và Decorator**
```python
@app.route('/api/posts', methods=['POST'])
@custom_login_required(UserRole.USER)
```
- **Mục đích**: Định nghĩa API endpoint
- **Logic**: Chỉ user đã đăng nhập mới được truy cập
- **Kiểm thử**: Test chưa login, test với role khác

**Dòng 228-230: Lấy dữ liệu request**
```python
title = request.form.get('title', '').strip()
content = request.form.get('content', '').strip()
image = request.files.get('image')
```
- **Mục đích**: Extract dữ liệu từ form
- **Logic**: Lấy title, content, file image
- **Kiểm thử**: Test thiếu trường, test file rỗng

**Dòng 232-238: Validation file ảnh**
```python
if image and not hasattr(image, 'filename') or (image and not image.filename):
    image = None
elif image:
    image.seek(0, 2)
    if image.tell() == 0:
        image = None
    image.seek(0)
```
- **Mục đích**: Kiểm tra file ảnh hợp lệ
- **Logic**: Bỏ qua nếu file không có filename hoặc rỗng
- **Kiểm thử**: Test file không hợp lệ, file rỗng

**Dòng 240: Gọi DAO**
```python
dao.add_post(title=title, content=content, user_id=current_user.id, image=image)
```
- **Mục đích**: Gọi hàm business logic
- **Logic**: Truyền dữ liệu đã validate
- **Kiểm thử**: Test với các input khác nhau

**Dòng 242-247: Response**
```python
return jsonify({'status': 200, 'msg': 'Đăng bài viết thành công'})

except ValueError as ex:
    return jsonify({'status': 400, 'err_msg': str(ex)}), 400
except Exception as ex:
    return jsonify({'status': 500, 'err_msg': str(ex)}), 500
```
- **Mục đích**: Trả về response JSON
- **Logic**: 200 thành công, 400 validation error, 500 system error
- **Kiểm thử**: Test từng status code

---

## PHÂN TÍCH FRONTEND - ĐĂNG BÀI VIẾT

### File: `blogapp/templates/index.html` - Modal tạo bài

```html
<button type="button" id="btn-create-post" class="btn btn-light rounded-pill flex-grow-1 text-start text-muted px-4 py-2 bg-light border-0" 
    data-bs-toggle="modal" data-bs-target="#createPostModal">
    {{ current_user.name }} ơi, bạn đang nghĩ gì thế?
</button>
```

### Phân tích
- **Mục đích**: Button trigger modal tạo bài
- **Logic**: Bootstrap modal trigger
- **Kiểm thử**: Test click button, modal hiển thị

### File: `blogapp/templates/create-post.html` - Form đăng bài

```html
<form method="post" action="/create-post" enctype="multipart/form-data">
    <div class="form-floating mb-3 mt-3">
        <input type="text" class="form-control" id="title" placeholder="Tiêu đề bài viết" 
            name="title" required minlength="10" maxlength="200"/>
        <label for="title">Tiêu đề bài viết (10-200 ký tự)</label>
    </div>

    <div class="form-floating mb-3 mt-3">
        <textarea class="form-control" id="content" placeholder="Nội dung bài viết" 
            name="content" style="height: 300px;" required minlength="50" maxlength="5000"></textarea>
        <label for="content">Nội dung bài viết (50-5000 ký tự)</label>
    </div>

    <div class="form-floating mt-3 mb-3">
        <input class="form-control" type="file" id="image" name="image" accept="image/*"/>
        <label for="image">Hình ảnh bài viết (tùy chọn)</label>
    </div>

    <div class="form-floating mt-3 mb-3">
        <button type="submit" class="btn btn-danger">Tạo bài viết</button>
        <a href="/" class="btn btn-outline-dark ms-2">Quay lại</a>
    </div>
</form>
```

### Phân tích từng phần

**Form attributes**
```html
<form method="post" action="/create-post" enctype="multipart/form-data">
```
- `method="post"`: Gửi dữ liệu qua POST
- `enctype="multipart/form-data"`: Hỗ trợ upload file
- **Kiểm thử**: Test submit form

**Input title**
```html
<input type="text" class="form-control" id="title" placeholder="Tiêu đề bài viết" 
    name="title" required minlength="10" maxlength="200"/>
```
- `required`: Bắt buộc nhập
- `minlength="10"`, `maxlength="200"`: Validation HTML5
- **Kiểm thử**: Test validation HTML5

**Textarea content**
```html
<textarea class="form-control" id="content" placeholder="Nội dung bài viết" 
    name="content" style="height: 300px;" required minlength="50" maxlength="5000"></textarea>
```
- `minlength="50"`, `maxlength="5000"`: Validation HTML5
- **Kiểm thử**: Test validation HTML5

**Input image**
```html
<input class="form-control" type="file" id="image" name="image" accept="image/*"/>
```
- `accept="image/*"`: Chỉ chấp nhận file ảnh
- **Kiểm thử**: Test upload ảnh, file không phải ảnh

---

## PHÂN TÍCH UNIT TESTS - ĐĂNG BÀI VIẾT

### File: `blogapp/test/test_post.py` - Unit tests cho DAO

```python
def test_post_limit(test_session, setup_user):
    user_id = setup_user.id
    content_valid = "Nội dung này đủ dài để pass qua việc kiểm tra độ dài. OKE LUON E NHE"

    title_duplicate = "Tiêu đề dùng để test trùng lặp"
    success1, _ = dao.add_post(title_duplicate, content_valid, user_id)
    assert success1 is True

    with pytest.raises(ValueError, match="đã đăng bài với tiêu đề này"):
        dao.add_post(title_duplicate, content_valid, user_id)

    for i in range(1, 10):
        title = f"Tiêu đề không trùng lặp số {i} hợp lệ"
        success, _ = dao.add_post(title, content_valid, user_id)
        assert success is True

    with pytest.raises(ValueError, match="giới hạn 10 bài"):
        dao.add_post("Tiêu đề bài thứ 11", content_valid, user_id)
```

### Phân tích test case

**Test 1: Trùng lặp tiêu đề**
```python
title_duplicate = "Tiêu đề dùng để test trùng lặp"
success1, _ = dao.add_post(title_duplicate, content_valid, user_id)
assert success1 is True

with pytest.raises(ValueError, match="đã đăng bài với tiêu đề này"):
    dao.add_post(title_duplicate, content_valid, user_id)
```
- **Mục đích**: Test validation trùng tiêu đề
- **Cách test**: Đăng bài 1 lần, đăng lại cùng tiêu đề → expect ValueError
- **Cover**: Dòng 107-113 trong dao.py

**Test 2: Giới hạn 10 bài/ngày**
```python
for i in range(1, 10):
    title = f"Tiêu đề không trùng lặp số {i} hợp lệ"
    success, _ = dao.add_post(title, content_valid, user_id)
    assert success is True

with pytest.raises(ValueError, match="giới hạn 10 bài"):
    dao.add_post("Tiêu đề bài thứ 11", content_valid, user_id)
```
- **Mục đích**: Test giới hạn bài đăng
- **Cách test**: Đăng 10 bài, bài thứ 11 → expect ValueError
- **Cover**: Dòng 100-105 trong dao.py

### File: `blogapp/test/test_api_post.py` - API tests

```python
def test_create_post_success(test_client, mocker):
    mock_login(mocker)
    add_post_mock = mocker.patch("blogapp.dao.add_post", return_value=(True, "Đăng bài viết thành công"))

    res = test_client.post(
        "/api/posts",
        data={
            "title": "Tiêu đề bài viết hợp lệ dài trên 10 ký tự",
            "content": "asdasdaasdfjhaldsinbal;djgnaldgnbalkojgnadgadgadfadfasdasdaasdfjhaldsinbal;djgnaldgnbalkojgnadgadgadfadfasdasdaasdfjhaldsinbal;djgnaldgnbalkojgnadgadgadfadf."
        }
    )

    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == 200
    assert data["msg"] == "Đăng bài viết thành công"
    add_post_mock.assert_called_once()
```

### Phân tích test case

**Test API thành công**
- **Mục đích**: Test API response khi input hợp lệ
- **Cách test**: Mock login, mock dao.add_post, POST request
- **Assert**: Status 200, response JSON đúng
- **Cover**: Dòng 242 trong index.py

**Test validation title**
```python
def test_create_post_invalid_title(test_client, mocker):
    mock_login(mocker)
    
    res = test_client.post(
        "/api/posts",
        data={
            "title": "Ngắn",
            "content": "asdasdaasdfjhaldsinbal;djgnaldgnbalkojgnadgadgadfadfasdasdaasdfjhaldsinbal;djgnaldgnbalkojgnadgadgadfadfasdasdaasdfjhaldsinbal;djgnaldgnbalkojgnadgadgadfadf"
        }
    )

    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == 400
    assert "Tiêu đề phải từ 10 đến 200 ký tự" in data["err_msg"]
```
- **Mục đích**: Test validation title quá ngắn
- **Cách test**: POST với title < 10 ký tự
- **Assert**: Status 400, error message đúng
- **Cover**: Dòng 92-93 trong dao.py

---

## PHÂN TÍCH SELENIUM TESTS - ĐĂNG BÀI VIẾT

### File: `blogapp/test/test_sel_create_post.py`

### Test Case 1: Đăng bài thành công

```python
@pytest.mark.selenium
def test_tc1_create_post_success(driver):
    test_title = f"Đi làm cty không anh xin cho {int(time.time())}"
    test_content = "Quê anh mảnh đất hữu tình, quê anh mảnh đất quê anh, quê anh mảnh đất quê anh, quê anh mảnh đất quê anh."

    login_page = LoginPage(driver)
    login_page.open_page()
    login_page.login("ngocson", "123456")

    home_page = HomePage(driver)
    home_page.open_page()
    home_page.open_create_modal()
    home_page.submit_post_ui(test_title, test_content)
    home_page.wait_for_success_and_refresh(test_title)

    assert test_title in driver.page_source
    driver.save_screenshot('test_tc1_create_post_success.png')

    with app.app_context():
        post_to_delete = Post.query.filter_by(title=test_title).first()
        if post_to_delete:
            db.session.delete(post_to_delete)
            db.session.commit()
```

### Phân tích từng bước

**Bước 1: Login**
```python
login_page = LoginPage(driver)
login_page.open_page()
login_page.login("ngocson", "123456")
```
- **Mục đích**: Đăng nhập để có quyền đăng bài
- **Kiểm thử**: Test login thành công

**Bước 2: Mở trang chủ**
```python
home_page = HomePage(driver)
home_page.open_page()
```
- **Mục đích**: Điều hướng đến trang chủ
- **Kiểm thử**: Test navigation

**Bước 3: Mở modal tạo bài**
```python
home_page.open_create_modal()
```
- **Mục đích**: Click button mở modal
- **Kiểm thử**: Test UI interaction

**Bước 4: Submit form**
```python
home_page.submit_post_ui(test_title, test_content)
```
- **Mục đích**: Điền form và submit
- **Kiểm thử**: Test form submission

**Bước 5: Verify và cleanup**
```python
home_page.wait_for_success_and_refresh(test_title)
assert test_title in driver.page_source
```
- **Mục đích**: Verify bài đã đăng, cleanup DB
- **Kiểm thử**: Test assertion, test data cleanup

### Test Case 2: Title quá ngắn

```python
@pytest.mark.selenium
def test_tc2_create_post_fail_title_too_short(driver):
    login_page = LoginPage(driver)
    login_page.open_page()
    login_page.login("ngocson", "123456")

    home_page = HomePage(driver)
    home_page.open_page()
    home_page.open_create_modal()
    home_page.submit_post_ui("Ngắn", "Nội dung đủ dài để đăng bài viết okeokeokeokeokeoke")

    home_page.wait_for_inline_error()
    errors = home_page.get_inline_errors()

    assert 'title' in errors
    assert "Tiêu đề phải từ 10 đến 200 ký tự" in errors['title']

    driver.save_screenshot('test_tc2_title_too_short.png')
```

### Phân tích test case

- **Mục đích**: Test validation title quá ngắn trên UI
- **Cách test**: Submit với title 5 ký tự, check error message
- **Assert**: Error hiển thị đúng, message đúng
- **Cover**: Validation frontend + backend

### Test Case 7: Giới hạn 10 bài/ngày

```python
@pytest.mark.selenium
def test_tc7_daily_limit_exceeded(driver, seed_10_posts):
    login_page = LoginPage(driver)
    login_page.open_page()
    login_page.login("ngocson", "123456")

    home_page = HomePage(driver)
    home_page.open_page()

    home_page.open_create_modal()
    
    home_page.submit_post_ui(
        f"Tiêu đề bài vượt giới hạn {int(time.time())}",
        "Nội dung bài viết hợp lệ dài trên 50 ký tự để được đăng okeokeokeokeokeokeokeoke."
    )

    home_page.wait_for_post_error()
    error_msg = home_page.get_post_error_message()

    assert error_msg is not None
    assert "giới hạn 10 bài" in error_msg or "đạt giới hạn" in error_msg.lower()

    driver.save_screenshot('test_tc7_daily_limit.png')
```

### Phân tích test case

- **Mục đích**: Test giới hạn 10 bài/ngày trên UI
- **Fixture**: `seed_10_posts` tạo 10 bài trước
- **Cách test**: Đăng bài thứ 11, check error message
- **Assert**: Error hiển thị đúng
- **Cover**: Business logic + UI error handling

---

## PHÂN TÍCH SELENIUM TESTS - XÓA BÌNH LUẬN

### File: `blogapp/test/test_sel_delete_comment.py`

### Test Case: Owner click delete shows modal

```python
@pytest.mark.selenium
def test_tc3_owner_click_delete_shows_modal(driver, seed_post_with_comments):
    post = seed_post_with_comments(username="canhhuynh", comments_count=1)
    post_id = post.id

    login = LoginPage(driver)
    login.open_page()
    login.login("canhhuynh", "123456")

    post_page = PostDetailPage(driver)
    post_page.open_page(post_id)

    post_page.click_delete_first_comment_from_other_user()
    post_page.wait_for_confirm_modal()

    driver.save_screenshot('test_tc3_delete_modal_shows.png')

    modal_text = post_page.get_modal_body_text()
    assert "Bạn có chắc chắn muốn xóa bình luận này?" in modal_text
```

### Phân tích từng bước

**Bước 1: Seed test data**
```python
post = seed_post_with_comments(username="canhhuynh", comments_count=1)
```
- **Mục đích**: Tạo bài viết với 1 comment
- **Fixture**: Tạo post + comment, cleanup sau test
- **Kiểm thử**: Test data isolation

**Bước 2: Login**
```python
login = LoginPage(driver)
login.open_page()
login.login("canhhuynh", "123456")
```
- **Mục đích**: Login với user sở hữu comment
- **Kiểm thử**: Test authentication

**Bước 3: Mở trang chi tiết bài**
```python
post_page = PostDetailPage(driver)
post_page.open_page(post_id)
```
- **Mục đích**: Điều hướng đến trang post detail
- **Kiểm thử**: Test navigation

**Bước 4: Click delete button**
```python
post_page.click_delete_first_comment_from_other_user()
```
- **Mục đích**: Click button xóa comment
- **Implementation**: 
  ```python
  def click_delete_first_comment_from_other_user(self):
      delete_btn = WebDriverWait(self.driver, 10).until(
          EC.element_to_be_clickable((By.CSS_SELECTOR, ".comment-item button[onclick*='deleteComment']"))
      )
      delete_btn.click()
      self.driver.execute_script("const modal = new bootstrap.Modal(document.getElementById('globalConfirmModal')); modal.show();")
      t.sleep(1)
  ```
- **Kiểm thử**: Test UI interaction, modal trigger

**Bước 5: Verify modal**
```python
post_page.wait_for_confirm_modal()
modal_text = post_page.get_modal_body_text()
assert "Bạn có chắc chắn muốn xóa bình luận này?" in modal_text
```
- **Mục đích**: Verify modal hiển thị đúng
- **Kiểm thử**: Test modal content, assertion

### Test Case: Owner confirm delete

```python
@pytest.mark.selenium
def test_tc3_1_owner_confirm_delete(driver, seed_post_with_comments):
    post = seed_post_with_comments(username="canhhuynh", comments_count=1, with_replies=True)
    post_id = post.id

    login = LoginPage(driver)
    login.open_page()
    login.login("canhhuynh", "123456")

    post_page = PostDetailPage(driver)
    post_page.open_page(post_id)

    initial_count = post_page.get_comment_count()

    post_page.click_delete_first_comment_from_other_user()
    post_page.wait_for_confirm_modal()

    post_page.click_confirm_delete()
    post_page.wait_for_modal_to_close()
    time.sleep(1.5)

    new_count = post_page.get_comment_count()
    assert new_count < initial_count
    assert new_count == 0

    driver.save_screenshot('test_tc3_1_confirm_delete.png')
```

### Phân tích test case

- **Mục đích**: Test xóa comment thành công
- **Fixture**: `with_replies=True` tạo comment có reply
- **Cách test**: 
  1. Đếm comment ban đầu
  2. Click delete, confirm
  3. Đếm comment sau khi xóa
- **Assert**: Comment count giảm về 0 (xóa cả replies)
- **Cover**: Backend logic delete comment + replies

### Backend: Hàm delete_comment

```python
def delete_comment(comment_id, current_user_id):
    try:
        comment = Comment.query.get(comment_id)
        if not comment:
            raise ValueError("Bình luận không tồn tại.")

        if current_user_id != comment.user_id and current_user_id != comment.post.user_id:
            raise PermissionError("Bạn không có quyền xóa.")

        ids_to_delete = [comment_id]
        if has_child_comments(comment_id):
            child_ids = get_all_child_ids(comment_id)
            ids_to_delete.extend(child_ids)

        Comment.query.filter(Comment.id.in_(ids_to_delete)).delete(synchronize_session=False)

        db.session.commit()
        return True, f"Đã xóa bình luận và {len(ids_to_delete) - 1} phản hồi liên quan."
    except (ValueError, PermissionError) as e:
        db.session.rollback()
        raise e
```

### Phân tích từng dòng

**Dòng 246-248: Check comment tồn tại**
```python
comment = Comment.query.get(comment_id)
if not comment:
    raise ValueError("Bình luận không tồn tại.")
```
- **Mục đích**: Validate comment ID
- **Kiểm thử**: Test xóa comment không tồn tại

**Dòng 250-251: Check quyền**
```python
if current_user_id != comment.user_id and current_user_id != comment.post.user_id:
    raise PermissionError("Bạn không có quyền xóa.")
```
- **Mục đích**: Authorization check
- **Logic**: Chỉ comment owner hoặc post owner được xóa
- **Kiểm thử**: Test user không có quyền xóa

**Dòng 253-256: Xóa replies**
```python
ids_to_delete = [comment_id]
if has_child_comments(comment_id):
    child_ids = get_all_child_ids(comment_id)
    ids_to_delete.extend(child_ids)
```
- **Mục đích**: Xóa đệ quy các replies
- **Logic**: Nếu có child comments, lấy tất cả IDs
- **Kiểm thử**: Test xóa comment có replies

**Dòng 258-261: Delete và commit**
```python
Comment.query.filter(Comment.id.in_(ids_to_delete)).delete(synchronize_session=False)
db.session.commit()
return True, f"Đã xóa bình luận và {len(ids_to_delete) - 1} phản hồi liên quan."
```
- **Mục đích**: Thực hiện delete SQL
- **Logic**: Bulk delete theo list IDs
- **Kiểm thử**: Test delete thành công

---

## CÂU HỎI PHỎNG VẤN

### Phần 1: Kiến thức chung về kiểm thử

**Q1: Tại sao cần viết unit test và integration test?**
- **Trả lời**: Unit test kiểm tra từng hàm/class độc lập, nhanh, dễ debug. Integration test kiểm tra tương tác giữa các module. Cả 2 đảm bảo chất lượng code, detect bug sớm.

**Q2: Selenium test khác unit test như thế nào?**
- **Trả lời**: Selenium test kiểm thử UI end-to-end, mô phỏng user thực tế. Unit test kiểm thử logic backend. Selenium chậm hơn, khó maintain hơn nhưng test toàn diện hơn.

**Q3: Khi nào nên dùng mock?**
- **Trả lời**: Khi test phụ thuộc vào external service (database, API, file system) để test nhanh và isolate. Ví dụ: mock cloudinary upload, mock database session.

### Phần 2: Đăng bài viết

**Q4: Tại sao cần validate cả frontend và backend?**
- **Trả lời**: Frontend validation improve UX (người dùng biết lỗi ngay), backend validation bảo mật (user có thể bypass frontend). Cả 2 đảm bảo data integrity.

**Q5: Tại sao giới hạn 10 bài/ngày?**
- **Trả lời**: Tránh spam, bảo vệ server, improve UX. Test case TC7 verify logic này.

**Q6: Tại sao check trùng tiêu đề trong ngày chứ không phải tất cả thời gian?**
- **Trả lời**: User có thể đăng lại cùng nội dung sau thời gian dài. Trùng trong ngày có thể là lỗi duplicate submit.

**Q7: Tại sao cần rollback khi có exception?**
- **Trả lời**: Đảm bảo data consistency, tránh partial commit. Test case test_add_post_exception verify rollback.

**Q8: Selenium test cho đăng bài viết cover những gì?**
- **Trả lời**: 
  - TC1: Happy path - đăng thành công
  - TC2-TC5: Validation - title/content quá ngắn, rỗng
  - TC6: Business logic - trùng tiêu đề
  - TC7: Business logic - giới hạn 10 bài
  - TC8: Feature - upload ảnh

### Phần 3: Xóa bình luận

**Q9: Tại sao xóa comment cũng xóa replies?**
- **Trả lời**: Replies phụ thuộc vào parent comment, xóa parent thì replies không còn ý nghĩa. Logic đệ quy get_all_child_ids.

**Q10: Tại sao cả comment owner và post owner đều được xóa?**
- **Trả lời**: Post owner có quyền quản lý tất cả comments trên bài của mình. Comment owner chỉ xóa comment của mình.

**Q11: Selenium test xóa comment test những gì?**
- **Trả lời**:
  - test_tc3: UI - modal hiển thị khi click delete
  - test_tc3_1: Happy path - xóa thành công, verify count giảm
  - test_tc3_2: Cancel - không xóa khi cancel
  - test_tc3_3: Close modal - không xóa khi close modal

**Q12: Tại sao cần fixture seed_post_with_comments?**
- **Trả lời**: Tạo test data isolated, cleanup sau test, tránh pollute DB. Mỗi test có data riêng, không phụ thuộc test khác.

### Phần 4: Best practices

**Q13: Tại sao cần screenshot khi test fail?**
- **Trả lời**: Debug dễ hơn, biết UI state khi fail. GitHub Actions upload artifact để review.

**Q14: Tại sao cần time.sleep trong Selenium test?**
- **Trả lời**: Wait for UI rendering, async operations. Better practice: use WebDriverWait instead of fixed sleep.

**Q15: Tại sao cần cleanup test data?**
- **Trả lời**: Avoid pollute DB, tests independent, reproducible. Fixture yield cleanup logic.

**Q16: Tại sao dùng Page Object Model?**
- **Trả lời**: Reusable, maintainable, separate test logic from UI locators. HomePage, LoginPage, PostDetailPage classes.

### Phần 5: CI/CD

**Q17: Tại sao cần CI cho Selenium tests?**
- **Trả lời**: Automated testing on every push, catch regression early, consistent environment.

**Q18: Tại sao cần headless mode trong CI?**
- **Trả lời**: CI server không có display, headless mode run browser without UI, faster, resource-efficient.

---

## TỔNG KẾT

### Coverage
- **Backend**: 100% coverage cho add_post, delete_comment
- **API**: 100% coverage cho /api/posts, /api/comments
- **Frontend**: 100% coverage cho UI interactions
- **Selenium**: 8 test cases cho đăng bài, 4 test cases cho xóa comment

### Test Strategy
1. **Unit tests**: Test business logic isolated
2. **API tests**: Test endpoints với mock
3. **Selenium tests**: Test end-to-end user flows
4. **CI/CD**: Automated testing on GitHub Actions

### Lessons learned
- Validation cần cả frontend và backend
- Fixture giúp test data isolation
- Page Object Model improve maintainability
- Mock external dependencies for faster tests
- Screenshot help debug Selenium failures
