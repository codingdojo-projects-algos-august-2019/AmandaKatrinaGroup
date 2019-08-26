# conveniently, Flask has a jsonify function
from flask import render_template, request, redirect, session, url_for, flash, jsonify
from models import User, user_schema, update_user_schema,\
    Blog, blog_schema, blogs_schema,\
    Comment, comment_schema, Tag, BlogTag
from config import db, app
from dateutil.parser import parse
from werkzeug.utils import secure_filename
from operator import itemgetter

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
    blog_objs = Blog.query.all()
    blogs = blogs_schema.dump(blog_objs)
    for blog in blogs.data:
        blog['comments'] = len(blog['blog_comments'])
    blogs = sorted(blogs.data, key=itemgetter('comments'), reverse=True)
    return render_template('land.html', user=user, blogs=blogs)


# user functions
def show_user(id):
    user = User.query.get(id)
    return render_template('user.html', user=user)


def edit_user(id):
    if 'userid' not in session:
        return redirect('/')
    user = User.query.get(id)
    if user.id != session['userid']:
        return redirect('/')
    if request.method == 'POST':
        user_obj = update_user_schema.dump(request.form)
        validate_user_data = User.validate_user(user_obj.data)
        if validate_user_data:
            User.update_user(user_obj.data)
            return redirect('/users/{}'.format(id))
    return render_template('edit_user.html', user=user)


# blog functions
def show_blog(id):
    blog = Blog.query.get(id)
    return render_template('blog.html', blog=blog)


def show_blogs():
    blog_objs = Blog.query.all()
    blogs = blogs_schema.dump(blog_objs)
    for blog in blogs:
        blog['comments'] = len(blog.blog_comments)
    return render_template('land.html', blogs=blogs.data)


def show_blogs_by_tag(tag):
    blogs = []
    blog_tags = None
    tag_obj = Tag.query.filter_by(text=tag).first()
    if tag_obj:
        blog_tags = BlogTag.query.filter_by(tag_id=tag_obj.id).all()
    if blog_tags:
        for blog in blog_tags:
            blogs.append(Blog.query.get(blog.blog_id))
    return render_template('index.html', blogs=blogs)


def create_blog():
    if 'userid' not in session:
        flash('Must be logged in to create blog', 'error')
        return redirect('/')
    if request.method == 'POST':
        tags = None
        if len(request.form['tags']) > 0:
            tags = [x.strip() for x in request.form['tags'].split(',')]
        validate_blog = Blog.validate_blog(request.form)
        if validate_blog:
            blog_data = blog_schema.dump(request.form)
            blog_data.data['content'] = request.form['editordata']
            blog_data.data['user_id'] = session['userid']
            new_blog = Blog.create_blog(blog_data.data)
            if tags:
                Tag.create_tags(data={'tags': tags, 'blog': new_blog.id})
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file and allowed_file(file.filename):
                filename = '{}_'.format(new_blog.id) + secure_filename(file.filename)
                file.save(os.path.join(app.config['BLOG_UPLOAD_FOLDER'], filename))
                Blog.update_picture(data={'id': new_blog.id, 'filepath': filename})
            return redirect('/blogs/{}'.format(new_blog.id))
    return render_template('create_blog.html')


def edit_blog(id):
    if 'userid' not in session:
        return redirect('/')
    blog = Blog.query.get(id)
    if blog.user_id != session['userid']:
        flash('You cannot edit this blog', 'warning')
        return redirect('/blogs/{}'.format(id))
    if request.method == 'POST':
        tags = None
        validate_blog = blog_schema.dump(request.form)
        if validate_blog:
            if blog.blog_has_tags:
                BlogTag.query.filter_by(blog_id=id).delete()
            if len(request.form['tags']) > 0:
                tags = [x.strip() for x in request.form['tags'].split(',')]
            if tags:
                Tag.create_tags(data={'tags': tags, 'blog': id})
            if request.files['file']:
                if blog.pic_filepath is not None:
                    delete_blog_picture(blog.pic_filepath)
                file = request.files['file']
                if file and allowed_file(file.filename):
                    filename = '{}_'.format(id) + secure_filename(file.filename)
                    file.save(os.path.join(app.config['BLOG_UPLOAD_FOLDER'], filename))
                    Blog.update_picture(data={'id': id, 'filepath': filename})
            blog.content = request.form['editordata']
            blog.title = request.form['title']
            db.session.commit()
        return redirect('/blogs/{}'.format(id))
    blog.tags = ''
    for i, tag in enumerate(blog.blog_has_tags):
        if i == 0:
            blog.tags += tag.tag.text
        else:
            blog.tags += ', ' + tag.tag.text
    return render_template('edit_blog.html', blog=blog)


def delete_blog(id):
    if 'userid' not in session:
        return redirect('/')
    blog = Blog.query.get(id)
    if blog.user_id != session['userid']:
        flash('You cannot delete this blog', 'error')
        return redirect('/')
    if blog.pic_filepath:
        delete_blog_picture(blog.pic_filepath)
    db.session.delete(blog)
    db.session.commit()
    return redirect('/')


# comment functions
def add_comment(id):
    if 'userid' not in session:
        return redirect('/')
    comment_data = comment_schema.dump(request.form)
    comment_data.data['user_id'] = session['userid']
    comment_data.data['blog_id'] = id
    validate_comment = Comment.validate_comment(comment_data.data)
    if validate_comment:
        Comment.create_comment(comment_data.data)
    return redirect('/blogs/{}'.format(id))


def delete_comment(id):
    if 'userid' not in session:
        return redirect('/')
    comment = Comment.query.get(id)
    if comment.user_id != session['userid']:
        flash('You cannot delete this comment', 'error')
        return redirect('/blogs/{}'.format(id))
    db.session.delete(comment)
    db.session.commit()
    return redirect('/blogs/{}'.format(id))


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


def delete_blog_picture(filename):
    delete_file = secure_filename(filename)
    os.remove(os.path.join(app.config['BLOG_UPLOAD_FOLDER'], delete_file))
    return


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
            os.remove(os.path.join(app.config['BLOG_UPLOAD_FOLDER'], delete_file))
        filename = '{}_'.format(blog.id) + secure_filename(file.filename)
        file.save(os.path.join(app.config['BLOG_UPLOAD_FOLDER'], filename))
        Blog.update_picture(data={'id': id, 'filename': filename})
        return redirect('/blogs/{}'.format(id))