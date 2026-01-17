#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
from sqlalchemy.exc import IntegrityError
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return ''


# Flask-RESTful Routes

api = Api(app)


class ScientistsListResource(Resource):
    def get(self):
        scientists = Scientist.query.all()
        return [scientist.to_dict(rules=('-missions',)) for scientist in scientists]

    def post(self):
        data = request.get_json()
        try:
            scientist = Scientist(
                name=data['name'],
                field_of_study=data['field_of_study']
            )
            db.session.add(scientist)
            db.session.commit()
            return scientist.to_dict(), 201
        except (KeyError, ValueError, IntegrityError):
            return {'errors': ['validation errors']}, 400


class ScientistResource(Resource):
    def get(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return {'error': 'Scientist not found'}, 404
        return scientist.to_dict()

    def patch(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return {'error': 'Scientist not found'}, 404
        data = request.get_json()
        try:
            if 'name' in data:
                scientist.name = data['name']
            if 'field_of_study' in data:
                scientist.field_of_study = data['field_of_study']
            db.session.commit()
            return scientist.to_dict(), 202
        except (ValueError, IntegrityError):
            return {'errors': ['validation errors']}, 400

    def delete(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return {'error': 'Scientist not found'}, 404
        db.session.delete(scientist)
        db.session.commit()
        return '', 204


class PlanetsListResource(Resource):
    def get(self):
        planets = Planet.query.all()
        return [planet.to_dict(rules=('-missions',)) for planet in planets]


class MissionsResource(Resource):
    def post(self):
        data = request.get_json()
        try:
            mission = Mission(
                name=data['name'],
                scientist_id=data['scientist_id'],
                planet_id=data['planet_id']
            )
            db.session.add(mission)
            db.session.commit()
            return mission.to_dict(), 201
        except (KeyError, ValueError, IntegrityError):
            return {'errors': ['validation errors']}, 400


api.add_resource(ScientistsListResource, '/scientists')
api.add_resource(ScientistResource, '/scientists/<int:id>')
api.add_resource(PlanetsListResource, '/planets')
api.add_resource(MissionsResource, '/missions')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
