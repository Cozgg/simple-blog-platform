from flask_login import login_required, current_user

from blogapp import app, login, dao
from flask import render_template, request, jsonify

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/comments', methods=['POST'])
@login_required
def add_comment():
    content = request.json.get('content')
    post_id = request.json.get('post_id')

    try:
        dao.save_comment(content=content, post_id=post_id, user_id=current_user.id)
        return jsonify({
            "status": 201,
            "msg": "Đã đăng tải thành công bình luận",
        })
    except PermissionError as e:
        return jsonify({
            "status": 400,
            "err_msg": str(e)
        })
    except Exception as ex:
        return jsonify({
            "status": 500,
            "err_msg": "Lỗi hệ thống không xác định"
        })

if __name__ == '__main__':
    app.run(debug=True)