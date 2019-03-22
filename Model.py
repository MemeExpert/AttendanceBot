from flask import Flask
from marshmallow import Schema, fields, pre_load, validate
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

ma = Marshmallow()
db = SQLAlchemy()


class Event(db.Model):
    __tablename = "events"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    creation_date = db.Column(db.TIMESTAMP,
                              server_default=db.func.current_timestamp(),
                              nullable=False)
    creator_id = db.Column(db.Integer,
                           db.ForeignKey('users.id', ondelete='CASCADE'),
                           nullable=False)
    creator = db.relationship('User',
                              backref=db.backref('events', lazy='dynamic'))


class Signup(db.Model):
    __tablename = "signups"
    id = db.Column(db.Integer, primary_key=True)
    signup_date = db.Column(db.TIMESTAMP,
                            server_default=db.func.current_timestamp(),
                            nullable=False)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id', ondelete='CASCADE'),
                        nullable=False)
    user = db.relationship('User',
                           backref=db.backref('signups', lazy='dynamic'))
    event_id = db.Column(db.Integer,
                         db.ForeignKey('events.id', ondelete='CASCADE'),
                         nullable=False)
    event = db.relationship('Event',
                            backref=db.backref('signups', lazy='dynamic'))


class Vote(db.Model):
    __tablename = "votes"
    id = db.Column(db.Integer, primary_key=True)
    vote_date = db.Column(db.TIMESTAMP,
                          server_default=db.func.current_timestamp(),
                          nullable=False)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id', ondelete='CASCADE'),
                        nullable=False)
    user = db.relationship('User',
                           backref=db.backref('votes', lazy='dynamic'))
    option_id = db.Column(db.Integer,
                          db.ForeignKey('poll_options.id', ondelete='CASCADE'),
                          nullable=False)
    option = db.relationship('Poll_Options',
                             backref=db.backref('votes', lazy='dynamic'))


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
                        db.ForeignKey('Poll.id', ondelete='CASCADE'),
                        nullable=False)
    index = db.Column(db.Integer, nullable=False)
    poll = db.relationship('Poll',
                           backref=db.backref('poll_options', lazy='dynamic'))


class User(db.Model):
    __tablename = "users"
    id = db.Column(db.Integer, primary_key=True)
    discordName = db.Column(db.String(150))
    slackName = db.Column(db.String(150))
    displayName = db.Column(db.String(150))
