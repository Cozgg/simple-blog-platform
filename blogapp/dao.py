from blogapp import db
from blogapp.models import Post, User, UserRole


def get_users(id = None):
    query = User.query
    if id:
        return query.get(id)
    return query.all()

def get_posts(id = None):
    query = Post.query
    if id:
        return query.get(id)
    return query.all()

def delete_post(post_id, current_user, is_confirmed=False):
    p = Post.query.get(post_id)
    if not p:
        raise ValueError('Bài viết ko tồn tại')

    if current_user.user_role != UserRole.ADMIN or p.user_id != current_user.id:
        raise PermissionError('Chỉ admin hoặc tác giả mới được xóa')

    if p.is_pinned:
        raise ValueError('Bài viết đang ghim ko được xóa')

    if p.comments > 10 and not is_confirmed:
        raise ValueError('Bài viết có hơn 10 bình luận, cần xác nhận xóa')

    db.session.delete(p)
    db.session.commit()
