from flask import request
from flask_restful import Resource
from Model import db, Signup, SignupSchema, Event, User
from flask_marshmallow import Marshmallow

ma = Marshmallow()


class SignupResource(Resource):
    def get(self):
        signup_schema = SignupSchema(many=True)
        query = Signup.query

        if 'id' in request.args:
            query = query.filter_by(id=request.args['id'])

        if 'user_id' in request.args:
            query = query.filter_by(user_id=request.args['user_id'])

        if 'event_id' in request.args:
            query = query.filter_by(event_id=request.args['event_id'])

        if 'response' in request.args:
            query = query.filter_by(response=request.args['response'])

        if 'userDisplayName' in request.args:
            query = query.join(User).filter(User.displayName == request.args['userDisplayName'])

        if 'eventName' in request.args:
            query = query.join(Event).filter(Event.title == request.args['eventName'])

        print(query)
        signups = Signup.query.all()
        signups = signup_schema.dump(query)
        if not signups:
            return {'message': 'Nothing found'}, 404
        return {'status': 'success', 'data': signups}, 200

    def post(self):
        signup_schema = SignupSchema()
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400

        # Validate and deserialize input
        data = signup_schema.load(json_data)
        # if errors:
        #    return errors, 422
        signup = Signup.query.filter_by(user_id=data['user_id'],
                                        event_id=data['event_id']).first()
        if signup:
            return {'message': 'Signup already exists'}, 400
        signup = Signup(
            user_id=data['user_id'],
            event_id=data['event_id'],
            response=data['response']
            )

        db.session.add(signup)
        db.session.commit()

        result = signup_schema.dump(signup)
        return {"status": 'success', 'data': result}, 201

    def put(self):
        signup_schema = SignupSchema()
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400
        # Validate and deserialize input
        data = signup_schema.load(json_data)
        # if errors:
        #    return errors, 422
        signup = Signup.query.filter_by(id=data['id']).first()
        if not signup:
            return {'message': 'Event does not exist'}, 400

        signup.user_id = data['user_id'],
        signup.event_id = data['event_id'],
        signup.response = data['response']

        db.session.commit()

        result = signup_schema.dump(signup)
        return {"status": 'success', 'data': result}, 204

    def delete(self):
        signup_schema = SignupSchema()
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400

        # Validate and deserialize input
        data = signup_schema.load(json_data)
        # if errors:
        #    return errors, 422
        signup = Signup.query.filter_by(id=data['id']).delete()
        db.session.commit()

        result = signup_schema.dump(signup)
        return {"status": 'success', 'data': result}, 204
