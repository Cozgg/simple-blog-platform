function submitComment(e) {
    e.preventDefault();
    const content = document.getElementById('comment-content').value;

    fetch('/api/comments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            content: content,
            post_id: window.postId
        })
    }).then(res => res.json()).then(data => {
        if (data.status === 201) {
            showToast(data.msg || 'Bình luận thành công!', 'success');
            document.getElementById('comment-content').value = '';
            setTimeout(() => location.reload(), 3000);
        } else {
            showToast(data.err_msg || 'Có lỗi xảy ra', 'danger');
        }
    }).catch(error => {
        showToast('Lỗi kết nối: ' + error.message, 'danger');
    });
}

function deleteComment(commentId) {
    showConfirmDialog('Xác nhận xóa', 'Bạn có chắc chắn muốn xóa bình luận này?', function() {
        fetch(`/api/comments/${commentId}`, {
            method: 'DELETE'
        }).then(res => res.json()).then(data => {
            if (data.status === 204) {
                showToast(data.msg || 'Đã xóa bình luận', 'success');
                document.querySelector(`[data-comment-id="${commentId}"]`).remove();
            } else {
                showToast(data.err_msg || 'Có lỗi xảy ra', 'danger');
            }
        }).catch(error => {
            showToast('Lỗi kết nối: ' + error.message, 'danger');
        });
    });
}

function deleteReply(replyId) {
    showConfirmDialog('Xác nhận xóa', 'Bạn có chắc chắn muốn xóa phản hồi này?', function() {
        fetch(`/api/comments/${replyId}`, {
            method: 'DELETE'
        }).then(res => res.json()).then(data => {
            if (data.status === 204) {
                showToast(data.msg || 'Đã xóa phản hồi', 'success');
                document.querySelector(`[data-reply-id="${replyId}"]`).remove();
            } else {
                showToast(data.err_msg || 'Có lỗi xảy ra', 'danger');
            }
        }).catch(error => {
            showToast('Lỗi kết nối: ' + error.message, 'danger');
        });
    });
}

function showReplyForm(commentId) {
    const replyForm = document.querySelector(`.reply-form[data-comment-id="${commentId}"]`);
    if (replyForm) replyForm.classList.remove('d-none');
}

function hideReplyForm(commentId) {
    const replyForm = document.querySelector(`.reply-form[data-comment-id="${commentId}"]`);
    if (replyForm) {
        replyForm.classList.add('d-none');
        replyForm.querySelector('.reply-textarea').value = '';
    }
}

function submitReply(commentId) {
    const replyForm = document.querySelector(`.reply-form[data-comment-id="${commentId}"]`);
    const content = replyForm.querySelector('.reply-textarea').value;

    if (content.length < 5) {
        showToast('Phản hồi phải có ít nhất 5 ký tự', 'warning');
        return;
    }

    fetch('/api/comments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            content: content,
            post_id: window.postId,
            parent_id: commentId
        })
    }).then(res => res.json()).then(data => {
        if (data.status === 201) {
            showToast(data.msg || 'Đã gửi phản hồi', 'success');
            replyForm.classList.add('d-none');
            setTimeout(() => location.reload(), 3000);
        } else {
            showToast(data.err_msg || 'Có lỗi xảy ra', 'danger');
        }
    }).catch(error => {
        showToast('Lỗi kết nối: ' + error.message, 'danger');
    });
}