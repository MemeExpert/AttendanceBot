from flask import request
from flask_restful import Resource
from Model import db, User, UserSchema
from flask_marshmallow import Marshmallow

user_schema = UserSchema()
ma = Marshmallow()


class UserResource(Resource):
    def get(self):
        users = User.query.all()
        users = user_schema.dump(users).data
        return {'status': 'success', 'data': users}, 200

    def post(self):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400

        # Validate and deserialize input
        data = user_schema.load(json_data, partial=False)
        user = User.query.filter_by(discordName=data['discordName']).first()
        if user:
            return {'message': 'User already exists'}, 400
        user = User(
            displayName=json_data['displayName'],
            discordName=json_data['discordName'],
            slackName=json_data['slackName']
            )

        db.session.add(user)
        db.session.commit()

        result = user_schema.dump(user)
        return {"status": 'success', 'data': result}, 201
