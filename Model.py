from flask import Flask
from marshmallow import Schema, fields, pre_load, validate
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

ma = Marshmallow()
db = SQLAlchemy()


class User(db.Model):
    __tablename = "users"
    id = db.Column(db.Integer, primary_key=True)
    discordName = db.Column(db.String(150))
    slackName = db.Column(db.String(150))
    displayName = db.Column(db.String(150))

    def __init__(self, id, discordName, slackName, displayName):
        self.id = id
        self.discordName = discordName
        self.slackName = slackName
        self.displayName = displayName


class Event(db.Model):
    __tablename = "events"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    creation_date = db.Column(db.TIMESTAMP,
                              server_default=db.func.current_timestamp(),
                              nullable=False)
    occurence_date = db.Column(db.TIMESTAMP,
                               server_default=db.func.current_timestamp(),
                               nullable=False)
    creator_id = db.Column(db.Integer,
                           db.ForeignKey(User.id, ondelete='CASCADE'),
                           nullable=False)
    creator = db.relationship('User',
                              backref=db.backref('events', lazy='dynamic'))

    def __init__(self, id, title, creation_date, occurence_date, creator_id):
        self.id = id
        self.title = title
        self.creation_date = creation_date
        self.occurence_date = occurence_date
        self.creator_id = creator_id


class Signup(db.Model):
    __tablename = "signups"
    id = db.Column(db.Integer, primary_key=True)
    signup_date = db.Column(db.TIMESTAMP,
                            server_default=db.func.current_timestamp(),
                            nullable=False)
    user_id = db.Column(db.Integer,
                        db.ForeignKey(User.id, ondelete='CASCADE'),
                        nullable=False)
    user = db.relationship('User',
                           backref=db.backref('signups', lazy='dynamic'))
    event_id = db.Column(db.Integer,
                         db.ForeignKey(Event.id, ondelete='CASCADE'),
                         nullable=False)
    event = db.relationship('Event',
                            backref=db.backref('signups', lazy='dynamic'))


class Poll(db.Model):
    __tablename = "polls"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    creation_date = db.Column(db.TIMESTAMP,
                              server_default=db.func.current_timestamp(),
                              nullable=False)


class Poll_Options(db.Model):
    __tablename = "poll_options"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(75), nullable=False)
    poll_id = db.Column(db.Integer,
                        db.ForeignKey(Poll.id, ondelete='CASCADE'),
                        nullable=False)
    index = db.Column(db.Integer, nullable=False)
    poll = db.relationship('Poll',
                           backref=db.backref('poll_options', lazy='dynamic'))


class Vote(db.Model):
    __tablename = "votes"
    id = db.Column(db.Integer, primary_key=True)
    vote_date = db.Column(db.TIMESTAMP,
                          server_default=db.func.current_timestamp(),
                          nullable=False)
    user_id = db.Column(db.Integer,
                        db.ForeignKey(User.id, ondelete='CASCADE'),
                        nullable=False)
    user = db.relationship('User',
                           backref=db.backref('votes', lazy='dynamic'))
    option_id = db.Column(db.Integer,
                          db.ForeignKey(Poll_Options.id, ondelete='CASCADE'),
                          nullable=False)
    option = db.relationship('Poll_Options',
                             backref=db.backref('votes', lazy='dynamic'))


class UserSchema(ma.Schema):
    id = fields.Integer()
    displayName = fields.String(required=True, validate=validate.Length(1))
    slackName = fields.String(required=True, validate=validate.Length(1))
    discordName = fields.String(required=True, validate=validate.Length(1))


class EventSchema(ma.Schema):
    id = fields.Integer()
    title = fields.String(required=True)
    creation_date = fields.DateTime()
    occurence_date = fields.DateTime(required=True)
    creator_id = fields.Integer(required=True)


class SignupSchema(ma.Schema):
    id = fields.Integer()
    signup_date = fields.DateTime()
    user_id = fields.Integer(required=True)
    event_id = fields.Integer(required=True)


class VoteSchema(ma.Schema):
    id = fields.Integer()
    vote_date = fields.DateTime()
    user_id = fields.Integer(required=True)
    vote_id = fields.Integer(required=True)


class PollSchema(ma.Schema):
    id = fields.Integer()
    title = fields.String(required=True, validate=validate.Length(1))
    creation_date = fields.DateTime()


class Poll_OptionsSchema(ma.Schema):
    id = fields.Integer()
    title = fields.String(required=True, validate=validate.Length(1))
    creation_date = fields.DateTime()

