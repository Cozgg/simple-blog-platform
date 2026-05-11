
import math
from flask_login import current_user, logout_user, login_user, login_required
from blogapp.decorators import login_required as custom_login_required
from blogapp import app, dao, login
from flask import render_template, jsonify, request, redirect
from blogapp.models import UserRole


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)

def register_routers(app):
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

        if len(content) < 5:
            return jsonify({
                "status": 400,
                "err_msg": "Nội dung của bình luận tối thiểu 5 kí tự"
            })

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

    @app.route('/api/comments/<int:comment_id>', methods=['DELETE'])
    @login_required
    def delete_comment_api(comment_id):
        try:
            success, message = dao.delete_comment(comment_id, current_user.id)
            return jsonify({
                "status": 204,
                "msg": message
            })

        except ValueError as e:
            return jsonify({
                "status": 404,
                "err_msg": str(e)
            })
        except PermissionError as e:
            return jsonify({
                "status": 403,
                "err_msg": str(e)
            })
        except Exception as ex:
            return jsonify({
                "status": 500,
                "err_msg": "Lỗi hệ thống không xác định"
            })

    @app.route('/post-detail/<int:post_id>', methods=['GET'])
    def post_detail_view(post_id):
        p = dao.get_posts(id=post_id)
        return render_template('post-detail.html', post=p)

    @app.route('/login', methods=['GET', 'POST'])
    def login_view():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            user = dao.auth_user(username=username, password=password)
            if user:
                login_user(user=user)
                next = request.args.get('next')
                return redirect(next if next else '/')
            
            return render_template('login.html', err_msg='Sai tên đăng nhập hoặc mật khẩu!')
        
        return render_template('login.html')

    @app.route('/logout')
    def logout_process():
        logout_user()
        return redirect('/login')

    @app.route('/register', methods=['GET', 'POST'])
    def register_view():
        if request.method == 'POST':
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
                
        return render_template('register.html')

    @app.route('/create-post', methods=['GET', 'POST'])
    @login_required
    def create_post_view():
        if request.method == 'POST':
            pass
        return render_template('create-post.html')

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
            is_firmed_str = request.args.get('confirmed', 'false').lower()
            is_firmed = (is_firmed_str == 'true')
            dao.delete_post(post_id=post_id, current_user=current_user, is_confirmed=is_firmed)
            return jsonify({
                'status': 204,
                "msg": "Xóa thành công"
            })

        except Exception as e:
            return jsonify({
                'status' : 400,
                'err_msg': str(e)
            })

if __name__ == '__main__':
    from blogapp import admin
    register_routers(app=app)
    app.run(debug=True)