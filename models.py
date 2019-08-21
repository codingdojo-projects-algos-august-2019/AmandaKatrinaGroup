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
                # if we get True after checking the password, we may put the user id in session
                db.session.commit()
                return result
        return False
    # TODO: Might add some sort of user active area


class UserSchema(Schema):
    id = fields.Integer()
    first_name = fields.String()
    last_name = fields.String()
    email = fields.String()
    password = fields.String()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    """ here you would add any schemas of keys 
    messages = fields.Nested('MessageSchema', many=True)
    -- On whatever you are nesting if this Schema is part of that Schema
    you need to use exclude=['messages']
    """


# might use schema for more later
user_schema = UserSchema()
users_schema = UserSchema(many=True, exclude=['password'])


class BreakupRequest(db.Model):
    __tablename__ = "breakup_requests"
    id = db.Column(db.Integer, primary_key=True)
    request_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    request_user = db.relationship('User', foreign_keys=[request_user_id],
                                   backref=backref("user_requests", cascade="all,delete"))
    recipient_name = db.Column(db.String(45))
    recipient_gender = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    # relationship
    reasons_for_breakup = db.relationship('Tag', secondary="breakup_tags")


class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())


class BreakupRequestTags(db.Model):
    __tablename__ = "breakup_tags"
    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=False)
    tag = db.relationship('Tag', foreign_keys=[tag_id],
                          backref=backref("reasons_to_breakup", cascade="all,delete"))
    request_id = db.Column(db.Integer, db.ForeignKey('breakup_requests.id'), nullable=False)


