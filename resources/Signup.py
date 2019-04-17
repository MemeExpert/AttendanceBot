from flask import request
from flask_restful import Resource
from Model import db, Signup, SignupSchema
from flask_marshmallow import Marshmallow

signup_schema = SignupSchema(many=True)
ma = Marshmallow()


class SignupResource(Resource):
    def get(self):
        query = Signup.query

        if 'id' in request.args:
            query = query.filter_by(id=request.args['id'])
            if not query:
                return {'message': 'Signup does not exist'}, 400

        if 'user_id' in request.args:
            query = query.filter_by(user_id=request.args['user_id'])
            if not query:
                return {'message': 'No signups with that user_id'}, 400

        if 'event_id' in request.args:
            query = query.filter_by(event_id=request.args['event_id'])
            if not query:
                return {'message': 'No signups with that event_id'}, 400

        if 'response' in request.args:
            query = query.filter_by(response=request.args['response'])
            if not query:
                return {'message': 'No signups with that response'}, 400

        print(query)
        signups = Signup.query.all()
        signups = signup_schema.dump(query)
        return {'status': 'success', 'data': signups}, 200

    def post(self):
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
