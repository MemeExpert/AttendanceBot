from flask import request
from flask_restful import Resource
from Model import db, User, UserSchema
from flask_marshmallow import Marshmallow

ma = Marshmallow()


class UserResource(Resource):
    def get(self):
        user_schema = UserSchema(many=True)
        query = User.query

        if 'id' in request.args:
            print("getting user by id")
            query = query.filter_by(id=request.args['id'])

        if 'discordUserId' in request.args:
            print("getting user by discordUserId")
            query = query.filter_by(discordUserId=request.args['discordUserId'])

        if 'slackName' in request.args:
            print("getting user by slackName")
            query = query.filter_by(slackName=request.args['slackName'])

        if 'displayName' in request.args:
            print("getting user by displayName")
            query = query.filter_by(displayName=request.args['displayName'])

        if len(request.args) == 0:
            return {'message': 'No parameters specified'}, 400

        # print(query)
        users = query.all()
        users = user_schema.dump(users)
        if not users:
            return {'message': 'Not found'}, 404

        return {'status': 'success', 'data': users}, 200

    def post(self):
        user_schema = UserSchema()
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400

        # Validate and deserialize input
        data = user_schema.load(json_data)
        # if errors:
        #    return errors, 422
        user = User.query.filter_by(discordUserId=data['discordUserId']).first()
        if user:
            return {'message': 'User already exists'}, 400
        user = User(
            displayName=json_data['displayName'],
            discordUserId=json_data['discordUserId'],
            slackName=json_data['slackName']
            )

        db.session.add(user)
        db.session.commit()

        result = user_schema.dump(user)
        return {"status": 'success', 'data': result}, 201

    def put(self):
        user_schema = UserSchema()
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400
        # Validate and deserialize input
        data = user_schema.load(json_data)
        # if errors:
        #    return errors, 422
        user = User.query.filter_by(id=data['id']).first()
        if not user:
            return {'message': 'User does not exist'}, 400

        user.displayName = data['displayName'],
        user.discordUserId = data['discordUserId'],
        user.slackName = data['slackName']

        db.session.commit()

        result = user_schema.dump(user)
        return {"status": 'success', 'data': result}, 204

    def delete(self):
        user_schema = UserSchema()
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400

        # Validate and deserialize input
        data = user_schema.load(json_data)
        # if errors:
        #    return errors, 422
        user = User.query.filter_by(id=data['id']).delete()
        db.session.commit()

        result = user_schema.dump(user)
        return {"status": 'success', 'data': result}, 204
