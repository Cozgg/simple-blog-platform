from flask_login import login_required, current_user

from blogapp import app, dao
from flask import render_template, jsonify, request

from blogapp.models import UserRole


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@login_required
def delete_posts(post_id):
    try:
        is_firmed = request.args.get('confirmed')

        dao.delete_post(post_id=post_id, current_user=current_user, is_confirmed=is_firmed)
        return jsonify({
            'status': 200,
            "msg": "Xóa thành công"
        })

    except Exception as e:
        return jsonify({
            'status' : 400,
            'err_msg': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)