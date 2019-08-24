# conveniently, Flask has a jsonify function
from flask import render_template, request, redirect, session, url_for, flash, jsonify
from models import User, user_schema, Blog, blog_schema, Comment, comment_schema
from config import db, app
from dateutil.parser import parse
from werkzeug.utils import secure_filename
import os


ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']

# error pages
def page_not_found(e):
    return render_template('404.html'), 404


app.register_error_handler(404, page_not_found)


def error_page(e):
    return render_template('500.html'), 500


app.register_error_handler(500, error_page)


def index():
    return redirect('/dashboard')


def register():
    validated_data = User.validate_user(request.form)
    if validated_data:
        user = user_schema.dump(request.form)
        create_user = User.register_user(user.data)
        if create_user:
            flash('User successfully added', 'success')
            return redirect('/')
        flash('There has been an error', 'error')
    return redirect('/')


def login():
    validated_data = User.validate_login_data(request.form)
    if validated_data:
        user = user_schema.dump(request.form)
        result = User.login_user(user.data)
        if result:
            session['userid'] = result.id
            return {'status': 'logged in'}
        return {'status': 'error'}
    return {'status': 'error'}


def logout():
    session.clear()
    return {'status': 'logged out'}


def dashboard(user=None):
    if 'userid' in session:
        user = User.query.get(session['userid'])
    blogs = Blog.query.all()
    for blog in blogs:
        blog.comments = len(blog.blog_comments)
    return render_template('land.html', user=user, blogs=blogs)


# blog functions
def show_blogs():
    blogs = Blog.query.all()
    return render_template('land.html', blogs=blogs)


def show_blog(id):
    blog = Blog.query.get(id)
    return render_template('blog.html', blog=blog)


def create_blog():
    if request.method == 'POST':
        tags = [x.strip() for x in request.form['tags'].split(',')]
        print(tags)
    return render_template('create_blog.html')


def edit_blog(id):
    if 'userid' not in session:
        return redirect('/')
    return redirect('/')


def delete_blog(id):
    if 'userid' not in session:
        return redirect('/')
    return redirect('/')


# extra functions
def check_email():
    email_exists = User.email_taken(request.form['email'])
    if email_exists['available']:
        return {'code': 'text-success', 'message': 'Email available'}
    return {'code': 'text-danger', 'message': email_exists['message']}


def parse_date(date_obj):
    return parse(date_obj)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_blog_picture(id):

    if 'userid' not in session:
        return redirect('/')
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        blog = Blog.query.get(id)
        if blog.profile_picture:
            delete_file = secure_filename(blog.profile_picture)
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], delete_file))
        filename = '{}_'.format(blog.id) + secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        Blog.update_picture(data={'id': id, 'filename': filename})
        return redirect('/blogs/{}'.format(id))