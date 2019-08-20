# conveniently, Flask has a jsonify function
from flask import render_template, request, redirect, session, url_for, flash, jsonify
from models import User, user_schema
from config import db, app
from dateutil.parser import parse


# error pages
def page_not_found(e):
    return render_template('404.html'), 404


app.register_error_handler(404, page_not_found)


def error_page(e):
    return render_template('500.html'), 500


app.register_error_handler(500, error_page)


def index():
    if 'userid' not in session:
        return render_template('login.html')
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
            return redirect('/dashboard')
        flash('You could not be logged in', 'error')
    return redirect('/')


def logout():
    session.clear()
    return redirect('/')


def dashboard():
    user_obj = User.query.get(session['userid'])
    user_obj_info = user_schema.dump(user_obj)
    return render_template('index.html', user=user_obj_info.data)


# extra functions
def check_email():
    email_exists = User.email_taken(request.form['email'])
    if email_exists['available']:
        return {'code': 'text-success', 'message': 'Email available'}
    return {'code': 'text-danger', 'message': email_exists['message']}


def parse_date(date_obj):
    return parse(date_obj)

