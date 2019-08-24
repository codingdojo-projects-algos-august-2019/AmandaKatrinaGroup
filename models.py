from config import db, bcrypt, ma
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from flask import session, flash
import re
from marshmallow import Schema, fields

email_validator = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
name_validator = re.compile(r'^[-a-zA-Z]+$')


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45))
    last_name = db.Column(db.String(45))
    email = db.Column(db.String(45))
    password = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    @classmethod
    def email_taken(cls, data):
        is_valid = False
        message = 'Enter a valid email'
        if email_validator.match(data):
            is_valid = True
            email_check = User.query.filter(User.email.ilike("%{}%".format(data))).first()
            if email_check:
                is_valid = False
                message = 'Email already exists'
        return {'available': is_valid, 'message': message}

    @classmethod
    def validate_user(cls, data):
        is_valid = True
        if len(data['first_name']) > 1:
            if not name_validator.match(data['first_name']):
                is_valid = False
                flash('First name can only contain letters', 'error')
        else:
            is_valid = False
            flash('First Name is required', 'error')
        if len(data['last_name']) > 1:
            if not name_validator.match(data['last_name']):
                is_valid = False
                flash('Last name can only contain letters', 'error')
        else:
            is_valid = False
            flash('Last Name is required', 'error')
        if len(data['password']) > 1:
            if data['password'] != data['confirm_password']:
                is_valid = False
                flash('Passwords must match', 'error')
        else:
            is_valid = False
            flash('Password must not be blank', 'error')
        if len(data['email']) > 1:
            if not email_validator.match(data['email']):
                is_valid = False
                flash('Enter valid email address', 'error')
        else:
            is_valid = False
            flash('Email must not be blank', 'error')
        return is_valid

    @classmethod
    def register_user(cls, data):
        data['password'] = bcrypt.generate_password_hash(data['password'])
        new_user = User(**data)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @classmethod
    def validate_login_data(cls, data):
        is_valid = True
        if len(data['email']) < 1:
            is_valid = False
            flash('Email field blank', 'error')
        if not email_validator.match(data['email']):
            is_valid = False
            flash('Enter valid email address', 'error')
        if len(data['password']) < 1:
            is_valid = False
            flash('Password field blank', 'error')
        return is_valid

    @classmethod
    def login_user(cls, data):
        result = User.query.filter(User.email.ilike("%{}%".format(data['email']))).first()
        if result:
            if bcrypt.check_password_hash(result.password, data['password']):
                return result
        return False


class UserSchema(Schema):
    id = fields.Integer()
    first_name = fields.String()
    last_name = fields.String()
    email = fields.String()
    password = fields.String()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


user_schema = UserSchema()


class Blog(db.Model):
    __tablename__ = "blogs"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', foreign_keys=[user_id], backref="user_blogs")
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    @classmethod
    def validate_blog(cls, data):
        is_valid = True
        if len(data['content']) < 5:
            is_valid = False
            flash('Blog must be 5 characters long', 'error')

        return is_valid

    @classmethod
    def create_blog(cls, data):
        new_blog = Blog(**data)
        db.session.add(new_blog)
        db.session.commit()
        return new_blog


class BlogSchema(Schema):
    id = fields.Integer()
    content = fields.String()
    user_id = fields.Integer()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


blog_schema = BlogSchema()


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    blog_id = db.Column(db.Integer, db.ForeignKey('blogs.id'), nullable=False)
    blog = db.relationship('Blog', foreign_keys=[blog_id], backref=backref("blog_comments", cascade="all, delete-orphan"))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', foreign_keys=[user_id],  backref=backref("user_comments", cascade="all, delete-orphan"))
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())


    @classmethod
    def validate_comment(cls, data):
        is_valid = True
        if len(data['content']) < 5:
            is_valid = False
            flash('Comment must be 5 characters long', 'error')

        return is_valid

    @classmethod
    def create_comment(cls, data):
        new_comment = Blog(**data)
        db.session.add(new_comment)
        db.session.commit()
        return new_comment


class CommentSchema(Schema):
    id = fields.Integer()
    content = fields.String()
    user_id = fields.Integer()
    blog_id = fields.Integer()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


comment_schema = CommentSchema()
