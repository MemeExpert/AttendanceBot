from flask import request
from flask_restful import Resource
from Model import db, Event, EventSchema, User
from flask_marshmallow import Marshmallow
from sqlalchemy import func

ma = Marshmallow()


class EventResource(Resource):
    def get(self):
        event_schema = EventSchema(many=True)
        query = Event.query.join(User, User.id == Event.creator_id)

        if 'id' in request.args:
            query = query.filter_by(id=request.args['id'])

        if 'creator_id' in request.args:
            query = query.filter_by(creator_id=request.args['creator_id'])

        if 'title' in request.args:
            query = query.filter(func.lower(Event.title) == func.lower(request.args['title']))

        if 'creatorDisplayName' in request.args:
            query = query.filter(func.lower(User.displayName) == func.lower(request.args['creatorDisplayName']))

        print(query)
        events = query.all()
        events = event_schema.dump(events)
        if not events:
            return {'message': 'Nothing found'}, 404
        return {'status': 'success', 'data': events}, 200

    def post(self):
        event_schema = EventSchema()
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400

        # Validate and deserialize input
        data = event_schema.load(json_data)
        # if errors:
        #    return errors, 422
        event = Event.query.filter_by(title=data['title'],
                                      occurence_date=data['occurence_date']).first()
        if event:
            return {'message': 'Event already exists'}, 400
        event = Event(
            title=data['title'],
            occurence_date=data['occurence_date'],
            creator_id=data['creator_id']
            )

        db.session.add(event)
        db.session.commit()

        result = event_schema.dump(event)
        return {"status": 'success', 'data': result}, 201

    def put(self):
        event_schema = EventSchema()
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400
        # Validate and deserialize input
        data = event_schema.load(json_data)
        # if errors:
        #    return errors, 422
        event = Event.query.filter_by(id=data['id']).first()
        if not event:
            return {'message': 'Event does not exist'}, 400

        event.title = data['title'],
        event.occurence_date = data['occurence_date'],
        event.creator_id = data['creator_id']

        db.session.commit()

        result = event_schema.dump(event)
        return {"status": 'success', 'data': result}, 204

    def delete(self):
        event_schema = EventSchema()
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400

        # Validate and deserialize input
        data = event_schema.load(json_data)
        # if errors:
        #    return errors, 422
        event = Event.query.filter_by(id=data['id']).delete()
        db.session.commit()

        result = event_schema.dump(event)
        return {"status": 'success', 'data': result}, 204
