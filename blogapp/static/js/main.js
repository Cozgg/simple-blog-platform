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

    btnYes.onclick = function() {
        callback();
        confirmModal.hide();
    };

    confirmModal.show();
}

function deletePost(postId, isConfirmed=false){
    fetch(`/api/posts/${postId}?confirmed=${isConfirmed}`,{
        method: 'delete',
        headers: {
            "Content-Type": "application/json"
        }
    }).then(res => res.json()).then(data =>{
        if(data.status === 204){
            showToast(data.msg, "success");
        }
        else if (data.err_msg === 'Bài viết có hơn 10 bình luận, cần xác nhận xóa') {
            showConfirmDialog(
                "Xác nhận xóa bài",
                "Bài viết này có nhiều bình luận. Bạn vẫn chắc chắn muốn xóa?",
                function() {
                    deletePost(postId, true);
                }
            );
        }else{
            showToast(data.err_msg, "danger");
        }
    }).catch(error => console.error('Error:', error));
}