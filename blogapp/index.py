import math

from flask_login import login_required, current_user, logout_user, login_user

from blogapp import app, dao, login
from flask import render_template, jsonify, request, redirect

from blogapp.models import UserRole

@app.route('/')
def index():
    page = int(request.args.get('page', 1))
    posts = dao.get_posts(page=page)
    return render_template('index.html', posts=posts,
                           pages=math.ceil(dao.count_posts()/ app.config['PAGE_SIZE']))

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


@app.route('/post-detail/<int:post_id>', methods=['GET'])
@login_required
def post_detail_view(post_id):
    p = dao.get_posts(id=post_id)
    return render_template('post-detail.html', post=p)

@app.route('/login')
def login_view():
    return render_template('login.html')


@app.route('/register')
def register_view():
    return render_template('register.html')

@app.route('/register', methods=['post'])
def register_process():
    data = request.form

    password = data.get('password')
    confirm = data.get('confirm')
    if password != confirm:
        err_msg = 'Mật khẩu không khớp!'
        return render_template('register.html', err_msg=err_msg)

    try:
        dao.add_user(name=data.get('name'), username=data.get('username'), password=password, avatar=request.files.get('avatar'))
        return redirect('/login')
    except ValueError as ex:
        return render_template("register.html", err_msg=str(ex))
    except Exception as ex:
        return render_template('register.html', err_msg=str(ex))



@app.route('/logout')
def logout_process():
    logout_user()
    return redirect('/login')


@app.route('/login', methods=['post'])
def login_process():
    username = request.form.get('username')
    password = request.form.get('password')

    user = dao.auth_user(username=username, password=password)
    if user:
        login_user(user=user)

    next = request.args.get('next')
    return redirect(next if next else '/')

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

@login.user_loader
def load_user(id):
    return dao.get_user_by_id(id)

if __name__ == '__main__':
    from blogapp import admin
    app.run(debug=True)