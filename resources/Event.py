from flask import request
from flask_restful import Resource
from Model import db, Event, EventSchema
from flask_marshmallow import Marshmallow

event_schema = EventSchema(many=True)
ma = Marshmallow()


class EventResource(Resource):
    def get(self):
        query = Event.query

        if 'id' in request.args:
            print("filtering event by id")
            query = query.filter_by(id=request.args['id'])
            if not query:
                return {'message': 'Event does not exist'}, 400

        if 'creator_id' in request.args:
            print("filtering event by creator_id")
            query = query.filter_by(creator_id=request.args['creator_id'])
            if not query:
                return {'message': 'No events created by specified user'}, 400

        if len(request.args) == 0:
            return {'message': 'No parameters specified'}, 400

        print(query)
        events = query.all()
        events = event_schema.dump(events)
        return {'status': 'success', 'data': events}, 200

    def post(self):
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
