from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask_jsonpify import jsonify
import pymysql
import config

# Init DB connection
db = pymysql.connect(config.DatabaseHost, config.DatabaseUser, config.DatabasePassword, config.DatabaseName)
sqlCursor = db.cursor()

# Setup flask API
app = Flask(__name__)
api = Api(app)

class Event(Resource):
    def get(self):
        query = sqlCursor.execute("select * from events") # This line performs query and returns json result
        return {'events': [i[0] for i in query.cursor.fetchall()]} # Return list of all event IDs

class Poll(Resource):
    def get(self):
        query = sqlCursor.execute("select * from polls") # This line performs query and returns json result
        return {'polls': [i[0] for i in query.cursor.fetchall()]} # Return list of all poll IDs


api.add_resource(Event, '/events')
api.add_resource(Poll, '/polls')
#api.add_resource(Vote, '/votes')


if __name__ == '__main__':
     app.run(port='5002')