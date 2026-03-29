from flask_login import current_user

from blogapp import app, login, dao
from flask import render_template, request, redirect, jsonify

from blogapp.decorators import login_required
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

@app.route('/register')
def register_view():
    return render_template('register.html')

@app.route('/register', methods = ['post'])
def register_process():
    password = request.form.get('password')


    return redirect('/login')


@app.route('/api/posts', methods=['POST'])
@login_required(UserRole.USER)
def create_post_api():
    try:
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        category_id = request.form.get('category_id')
        image = request.files.get('image')

        if not title or len(title) < 10 or len(title) > 200:
            return jsonify({'status': 400, 'err_msg': 'Tiêu đề phải từ 10 đến 200 ký tự'})

        if not content or len(content) < 50 or len(content) > 5000:
            return jsonify({'status': 400, 'err_msg': 'Nội dung phải từ 50 đến 5000 ký tự'})

        success, msg = dao.add_post(
            title=title,
            content=content,
            user_id=current_user.id,
            category_id=category_id,
            image=image
        )

        if success:
            return jsonify({'status': 200, 'msg': msg})

        return jsonify({'status': 400, 'err_msg': msg})

    except Exception as e:
        return jsonify({'status': 500, 'err_msg': str(e)})

@app.route('/login', methods = ['post'])
def login_process():

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)