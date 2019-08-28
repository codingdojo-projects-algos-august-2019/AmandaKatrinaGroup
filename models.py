from config import db, bcrypt
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from flask import flash
import re
from marshmallow import Schema, fields

email_validator = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
name_validator = re.compile(r'^[-a-zA-Z]+$')
username_validator = re.compile(r'^[.a-zA-Z]+$')
twitter_handle_validator = re.compile(r'^[_a-zA-Z0-9]+$')


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45))
    last_name = db.Column(db.String(45))
    tagline = db.Column(db.String(100))
    twitter = db.Column(db.String(15))
    instagram = db.Column(db.String(30))
    facebook = db.Column(db.String(50))
    email = db.Column(db.String(45))
    password = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    @classmethod
    def email_taken(cls, data):
        is_valid = False
        message = ''
        if len(data) > 0:
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

    @classmethod
    def validate_update_data(cls, data):
        is_valid = True
        if len(data['facebook']) > 0:
            if len(data['facebook']) < 5 or len(data['facebook']) > 50:
                is_valid = False
                flash('Facebook username must be between 5-50 characters', 'error')
            else:
                if not username_validator.match(data['facebook']):
                    is_valid = False
                    flash('Facebook username must contain letters, numbers, or period', 'error')
        if len(data['instagram']) > 0:
            if len(data['instagram']) > 30:
                is_valid = False
                flash('Instagram username must be less than 30 characters', 'error')
            else:
                if not username_validator.match(data['instagram']):
                    is_valid = False
                    flash('Instagram username must contain letters, numbers, or period', 'error')
        if len(data['twitter']) > 0:
            if len(data['twitter']) > 15:
                is_valid = False
                flash('Twitter handle must be less than 30 characters', 'error')
            else:
                if not twitter_handle_validator.match(data['twitter']):
                    is_valid = False
                    flash('Twitter handle must contain letters, numbers, or underscore', 'error')
        return is_valid

    @classmethod
    def update_user(cls, data):
        user = User.query.get(data['id'])
        if len(data['twitter']) > 0:
            user.twitter = data['twitter']
        if len(data['instagram']) > 0:
            user.twitter = data['instagram']
        if len(data['facebook']) > 0:
            user.twitter = data['facebook']
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.email = data['email']
        user.tagline = data['tagline']
        db.session.commit()
        return user


class UserSchema(Schema):
    id = fields.Integer()
    first_name = fields.String()
    last_name = fields.String()
    tagline = fields.String()
    twitter = fields.String()
    facebook = fields.String()
    instagram = fields.String()
    profile_picture = fields.String()
    email = fields.String()
    password = fields.String()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


# used to create a user
user_schema = UserSchema(exclude=['tagline', 'twitter', 'facebook', 'instagram', 'profile_picture'])


user_profile_schema = UserSchema(exclude=['password'])


class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    # relationships
    tag_has_blogs = relationship('BlogTag')

    @classmethod
    def create_tags(cls, data):
        for tag in data['tags']:
            tag_exists = Tag.query.filter_by(text=tag).first()
            if tag_exists:
                blog_tag = BlogTag(tag_id=tag_exists.id, blog_id=data['blog'])
                db.session.add(blog_tag)
            else:
                new_tag = Tag(text=tag)
                db.session.add(new_tag)
                db.session.commit()
                blog_tag = BlogTag(tag_id=new_tag.id, blog_id=data['blog'])
                db.session.add(blog_tag)
            db.session.commit()
        return


class TagSchema(Schema):
    id = fields.Integer()
    text = fields.String()


tag_schema = TagSchema()


class BlogTag(db.Model):
    __tablename__ = "blog_tags"
    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=False)
    blog_id = db.Column(db.Integer, db.ForeignKey('blogs.id'), nullable=False)

    # relationships
    tag = relationship('Tag', back_populates="tag_has_blogs")
    blog = relationship('Blog', back_populates="blog_has_tags")


class BlogTagSchema(Schema):
    tag = fields.Nested('TagSchema', only=['text'])


class Blog(db.Model):
    __tablename__ = "blogs"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(55))
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', foreign_keys=[user_id], backref="user_blogs")
    pic_filepath = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    # relationships
    blog_has_tags = relationship('BlogTag', cascade="all, delete-orphan")
    @classmethod
    def validate_blog(cls, data):
        is_valid = True
        if len(data['editordata']) < 10:
            is_valid = False
            flash('Blog content must be at least 10 characters long', 'error')
        if len(data['title']) < 5:
            is_valid = False
            flash('Blog title must be at least 5 characters long', 'error')
        return is_valid

    @classmethod
    def create_blog(cls, data):
        new_blog = Blog(**data)
        db.session.add(new_blog)
        db.session.commit()
        return new_blog

    @classmethod
    def update_picture(cls, data):
        blog = Blog.query.get(data['id'])
        blog.pic_filepath = data['filepath']
        db.session.commit()
        return


class BlogSchema(Schema):
    id = fields.Integer()
    content = fields.String()
    title = fields.String()
    pic_filepath = fields.String()
    user = fields.Nested(user_profile_schema)
    blog_comments = fields.Nested('CommentSchema', many=True)
    blog_has_tags = fields.Nested('BlogTagSchema', many=True)
    user_id = fields.Integer()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


blog_schema = BlogSchema()
blogs_schema = BlogSchema(many=True)


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
        new_comment = Comment(**data)
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






