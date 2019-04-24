from flask import Blueprint
from flask_restful import Api
from resources.User import UserResource
from resources.Event import EventResource
from resources.Signup import SignupResource

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# Route
api.add_resource(UserResource, '/user')
api.add_resource(EventResource, '/event')
api.add_resource(SignupResource, '/signup')
