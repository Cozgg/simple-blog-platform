from blogapp import db
from models import Comment
from sqlalchemy import desc
from datetime import datetime

def is_allow_to_comment(user_id, post_id):
    count_comment = Comment.query.filter_by(user_id=user_id, post_id = post_id).count()
    if count_comment >=5:
        return False, "Bạn đã đạt đến giới hạn bình luận cho bài viết này"

    last_comment = Comment.query.filter_by(user_id=user_id).order_by(desc(Comment.created_date)).first()

    if last_comment:
        gap = datetime.now() - last_comment.created_date
        if gap.total_seconds() < 10:
            wait = 10 - int(gap.total_seconds())
            return False, f"Vui lòng đợi sau {wait} giây để tiếp tục bình luận"
    return True, None

def save_comment(content, post_id, user_id):
    allow, message = is_allow_to_comment(user_id, post_id)
    if not allow:
        raise PermissionError(message)
    try:
        new_comment = Comment(content=content, post_id=post_id,user_id=user_id)
        db.session.add(new_comment)
        db.session.commit()
    except Exception as ex:
        db.session.rollback()