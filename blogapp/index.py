from flask_login import current_user, logout_user, login_user, login_required
from blogapp.decorators import login_required as custom_login_required

from blogapp import app, dao, login
from flask import render_template, jsonify, request, redirect
from blogapp.models import UserRole

@app.route('/')
def index():
    return render_template('index.html')

@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)

@app.route('/login')
def login_view():
    return render_template('login.html')

@app.route('/login', methods=['post'])
def login_process():
    username = request.form.get('username')
    password = request.form.get('password')

    user = dao.auth_user(username=username, password=password)
    if user:
        login_user(user=user)

    next = request.args.get('next')
    return redirect(next if next else '/')

@app.route('/logout')
def logout_process():
    logout_user()
    return redirect('/login')

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

@app.route('/api/posts', methods=['POST'])
@custom_login_required(UserRole.USER)
def create_post_api():
    try:
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        image = request.files.get('image')

        if not title or len(title) < 10 or len(title) > 200:
            return jsonify({'status': 400, 'err_msg': 'Tiêu đề phải từ 10 đến 200 ký tự'})

        if not content or len(content) < 50 or len(content) > 5000:
            return jsonify({'status': 400, 'err_msg': 'Nội dung phải từ 50 đến 5000 ký tự'})

        success, msg = dao.add_post(
            title=title,
            content=content,
            user_id=current_user.id,
            image=image
        )

        if success:
            return jsonify({'status': 200, 'msg': msg})

        return jsonify({'status': 400, 'err_msg': msg})

    except Exception as e:
        return jsonify({'status': 500, 'err_msg': str(e)})

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
    from blogapp import admin
    app.run(debug=True)