function submitComment(e) {
    e.preventDefault();
    const content = document.getElementById('comment-content').value;
    const errorDiv = document.getElementById('comment-error');
    const successDiv = document.getElementById('comment-success');

    errorDiv.classList.add('d-none');
    successDiv.classList.add('d-none');

    fetch('/api/comments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            content: content,
            post_id: window.postId
        })
    }).then(res => res.json()).then(data => {
        if (data.status === 201) {
            successDiv.textContent = data.msg;
            successDiv.classList.remove('d-none');
            document.getElementById('comment-content').value = '';
            setTimeout(() => location.reload(), 1000);
        } else {
            errorDiv.textContent = data.err_msg || 'Có lỗi xảy ra';
            errorDiv.classList.remove('d-none');
        }
    }).catch(error => {
        errorDiv.textContent = 'Lỗi kết nối: ' + error.message;
        errorDiv.classList.remove('d-none');
    });
}

function deleteComment(commentId) {
    if (!confirm('Bạn có chắc chắn muốn xóa bình luận này?')) return;

    fetch(`/api/comments/${commentId}`, {
        method: 'DELETE'
    }).then(res => res.json()).then(data => {
        if (data.status === 204) {
            alert(data.msg);
            document.querySelector(`[data-comment-id="${commentId}"]`).remove();
        } else {
            alert(data.err_msg || 'Có lỗi xảy ra');
        }
    }).catch(error => {
        alert('Lỗi kết nối: ' + error.message);
    });
}

function deleteReply(replyId) {
    if (!confirm('Bạn có chắc chắn muốn xóa phản hồi này?')) return;

    fetch(`/api/comments/${replyId}`, {
        method: 'DELETE'
    }).then(res => res.json()).then(data => {
        if (data.status === 204) {
            alert(data.msg);
            document.querySelector(`[data-reply-id="${replyId}"]`).remove();
        } else {
            alert(data.err_msg || 'Có lỗi xảy ra');
        }
    }).catch(error => {
        alert('Lỗi kết nối: ' + error.message);
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
    const errorDiv = replyForm.querySelector('.reply-error');

    if (content.length < 5) {
        errorDiv.textContent = 'Phản hồi phải có ít nhất 5 ký tự';
        errorDiv.classList.remove('d-none');
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
            errorDiv.classList.add('d-none');
            replyForm.classList.add('d-none');
            setTimeout(() => location.reload(), 500);
        } else {
            errorDiv.textContent = data.err_msg || 'Có lỗi xảy ra';
            errorDiv.classList.remove('d-none');
        }
    }).catch(error => {
        errorDiv.textContent = 'Lỗi kết nối: ' + error.message;
        errorDiv.classList.remove('d-none');
    });
}