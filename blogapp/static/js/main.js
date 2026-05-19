function showToast(message, type = 'success') {
    const toastElement = document.getElementById('liveToast');
    const toastBody = document.getElementById('toast-message');

    toastBody.innerText = message;

    toastElement.className = `toast align-items-center border-0 text-white bg-${type}`;

    const toast = new bootstrap.Toast(toastElement, {
        delay: 3000,
        animation: true
    });

    toast.show();
}

function showConfirmDialog(title, message, callback) {
    const modalEl = document.getElementById('globalConfirmModal');
    const titleEl = document.getElementById('confirmTitle');
    const msgEl = document.getElementById('confirmMessage');
    const btnYes = document.getElementById('btnConfirmYes');

    titleEl.innerText = title;
    msgEl.innerText = message;

    const confirmModal = new bootstrap.Modal(modalEl);

    btnYes.onclick = function () {
        callback();
        confirmModal.hide();
    };

    confirmModal.show();
}

function deletePost(postId, isConfirmed = false) {
    fetch(`/api/posts/${postId}?confirmed=${isConfirmed}`, {
        method: 'delete',
        headers: {
            "Content-Type": "application/json"
        }
    }).then(res => res.json()).then(data => {
        if (data.status === 204) {
            showToast(data.msg, "success");
            const postEl = document.getElementById(`post-${postId}`);
            if (postEl) postEl.remove();
        }
        else if (data.err_msg === 'Bài viết có hơn 10 bình luận, cần xác nhận xóa') {
            showConfirmDialog(
                "Xác nhận xóa bài",
                "Bài viết này có nhiều bình luận. Bạn vẫn chắc chắn muốn xóa?",
                function () {
                    deletePost(postId, true);
                }
            );
        } else {
            showToast(data.err_msg, "danger");
        }
    }).catch(error => console.error('Error:', error));
}

function submitPost(e) {
    e.preventDefault();
    const form = document.getElementById('createPostForm');
    const titleInput = document.getElementById('title');
    const contentInput = document.getElementById('content');
    const titleError = document.getElementById('title-error');
    const contentError = document.getElementById('content-error');
    const errorDiv = document.getElementById('post-error');
    const successDiv = document.getElementById('post-success');
    const submitBtn = form.querySelector('button[type="submit"]');

    if (errorDiv) errorDiv.classList.add('d-none');
    if (successDiv) successDiv.classList.add('d-none');
    if (titleError) titleError.classList.add('d-none');
    if (contentError) contentError.classList.add('d-none');

    const title = titleInput.value.trim();
    const content = contentInput.value.trim();
    let hasError = false;

    if (!title || title.length < 10) {
        if (titleError) {
            titleError.textContent = 'Tiêu đề phải từ 10 đến 200 ký tự';
            titleError.classList.remove('d-none');
        }
        hasError = true;
    }

    if (!content || content.length < 50) {
        if (contentError) {
            contentError.textContent = 'Nội dung phải từ 50 đến 5000 ký tự';
            contentError.classList.remove('d-none');
        }
        hasError = true;
    }

    if (hasError) return;

    const formData = new FormData(form);

    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Đang đăng...';
    }

    fetch('/api/posts', {
        method: 'POST',
        body: formData
    })
        .then(res => res.json())
        .then(data => {
            if (data.status === 200 || data.status === 201) {
                showToast(data.msg || 'Đăng bài viết thành công', 'success');
                form.reset();

                const modalEl = document.getElementById('createPostModal');
                if (modalEl) {
                    const modal = bootstrap.Modal.getInstance(modalEl);
                    if (modal) modal.hide();
                }

                if (window.location.pathname === '/') {
                    fetch('/')
                        .then(res => res.text())
                        .then(html => {
                            const parser = new DOMParser();
                            const doc = parser.parseFromString(html, 'text/html');
                            const newContainer = doc.getElementById('post-list-container');
                            const oldContainer = document.getElementById('post-list-container');
                            if (newContainer && oldContainer) {
                                oldContainer.innerHTML = newContainer.innerHTML;
                            }
                        });
                } else {
                    setTimeout(() => window.location.href = '/', 1000);
                }

            } else {
                if (errorDiv) {
                    errorDiv.textContent = data.err_msg || 'Có lỗi xảy ra';
                    errorDiv.classList.remove('d-none');
                } else {
                    showToast(data.err_msg || 'Có lỗi xảy ra', 'danger');
                }
            }
        })
        .catch(error => {
            if (errorDiv) {
                errorDiv.textContent = 'Lỗi kết nối: ' + error.message;
                errorDiv.classList.remove('d-none');
            } else {
                showToast('Lỗi kết nối: ' + error.message, 'danger');
            }
        })
        .finally(() => {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Đăng bài';
            }
        });
}