from marshmallow import fields, validate
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import BIGINT

ma = Marshmallow()
db = SQLAlchemy()


class User(db.Model):
    __tablename = "users"
    id = db.Column(db.Integer, primary_key=True)
    discordUserId = db.Column(BIGINT(unsigned=True), unique=True, nullable=False)
    slackName = db.Column(db.String(150))
    displayName = db.Column(db.String(150), nullable=False)

    def __init__(self, discordUserId, slackName, displayName):
        self.discordUserId = discordUserId
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
    announceMessageId = db.Column(BIGINT(unsigned=True), server_default="0", nullable=False)

    def __init__(self, title, occurence_date, creator_id):
        self.title = title
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
    response = db.Column(db.Integer, nullable=False)

    def __init__(self, user_id, event_id, response):
        self.user_id = user_id
        self.event_id = event_id
        self.response = response


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
    displayName = fields.Str()
    slackName = fields.Str()
    discordUserId = fields.Integer()

    class Meta:
        ordered = True


class EventSchema(ma.Schema):
    id = fields.Integer()
    title = fields.String()
    creation_date = fields.DateTime()
    occurence_date = fields.DateTime()
    announceMessageId = fields.Integer()
    creator_id = fields.Integer()
    creator = fields.Nested(UserSchema)

    class Meta:
        ordered = True


class SignupSchema(ma.Schema):
    id = fields.Integer()
    signup_date = fields.DateTime()
    response = fields.Integer()
    user_id = fields.Integer()
    event_id = fields.Integer()
    user = fields.Nested(UserSchema)
    event = fields.Nested(EventSchema)

    class Meta:
        ordered = True


class VoteSchema(ma.Schema):
    id = fields.Integer()
    vote_date = fields.DateTime()
    user_id = fields.Integer(required=True)
    vote_id = fields.Integer(required=True)

    class Meta:
        ordered = True


class PollSchema(ma.Schema):
    id = fields.Integer()
    title = fields.String(required=True, validate=validate.Length(1))
    creation_date = fields.DateTime()

    class Meta:
        ordered = True


class Poll_OptionsSchema(ma.Schema):
    id = fields.Integer()
    title = fields.String(required=True, validate=validate.Length(1))
    creation_date = fields.DateTime()

    class Meta:
        ordered = True
