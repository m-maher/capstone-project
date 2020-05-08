import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from auth import AuthError, requires_auth
from models import db_drop_and_create_all, setup_db, Actor, Movie, Performance
from config import pagination

PER_PAGE = pagination['example']


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                            'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                            'POST,GET,PATCH,DELETE,OPTIONS')
        return response

    def paginate(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * PER_PAGE
        end = start + PER_PAGE

        formatted = [object_name.format() for object_name in selection]
        return formatted[start:end]

    @app.route('/actors', methods=['GET'])
    @requires_auth('read:actors')
    def get_actors(payload):

        selection = Actor.query.all()
        actors = paginate(request, selection)

        if len(actors) == 0:
            abort(404, {'message': 'no actors found'})

        return jsonify({
            'success': True,
            'actors': actors
        })

    @app.route('/actors', methods=['POST'])
    @requires_auth('create:actors')
    def add_actors(payload):

        body = request.get_json()

        if not body:
            abort(400, {'message': 'request doesnt containt a valid JSON'})

        name = body.get('name', None)
        age = body.get('age', None)
        gender = body.get('gender', 'other')

        if not name:
            abort(422, {'message': 'no name provided'})

        if not age:
            abort(422, {'message': 'no age provided'})

        new_actor = (Actor(name=name, age=age, gender=gender))

        new_actor.insert()

        return jsonify({
            'success': True,
            'created': new_actor.id
        })

    @app.route('/actors/<actor_id>', methods=['PATCH'])
    @requires_auth('edit:actors')
    def edit_actors(payload, actor_id):

        body = request.get_json()

        if not actor_id:
            abort(400, {'message': 'append an actor id to request url'})

        if not body:
            abort(400, {'message': 'reuest doent contain a valid JSON'})

        actor_update = Actor.query.filter(Actor.id == actor_id).one_or_none()

        if not actor_update:
            abort(
                404, {'message': 'Actor with id {} not found in database'
                      .format(actor_id)})

        name = body.get('name', actor_update.name)
        age = body.get('age', actor_update.age)
        gender = body.get('gender', actor_update.gender)

        actor_update.name = name
        actor_update.age = age
        actor_update.gender = gender

        actor_update.update()

        return jsonify({
            'success': True,
            'updated': actor_update.id,
            'actor': [actor_update.format()]
        })

    @app.route('/actors/<actor_id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def delete_actors(payload, actor_id):

        if not actor_id:
            abort(400, {'message': 'append an actor id to request url'})

        actor_delete = Actor.query.filter(Actor.id == actor_id).one_or_none()

        if not actor_delete:
            abort(
                404, {'message': 'Actor with id {} not found in database'
                      .format(actor_id)})

        actor_delete.delete()

        return jsonify({
            'success': True,
            'deleted': actor_id
        })

    @app.route('/movies', methods=['GET'])
    @requires_auth('read:movies')
    def get_movies(payload):

        selection = Movie.query.all()
        movies = paginate(request, selection)

        if len(movies) == 0:
            abort(404, {'message': 'no movies found in database'})

        return jsonfiy({
            'success': True,
            'movies': movies
        })

    @app.route('/movies', methods=['POST'])
    @requires_auth('create:movies')
    def add_movies(payload):

        body = request.get_json()

        if not body:
            abort(400, {'message': 'request doesnt contain a valid JSON'})

        title = body.get('title', None)
        release_date = body.get('release_date', None)

        if not title:
            abort(422, {'message': 'no title provided'})

        if not release_date:
            abort(422, {'message': 'no release_date provided'})

        new_movie = (Movie(
            title=title,
            release_date=release_date
        ))

        new_movie.insert()

        return jsonfiy({
            'success': True,
            'creates': new_movie.id
        })

    @app.route('/movies/<movie_id>', methods=['PATCH'])
    @requires_auth('edit:movies')
    def edit_movies(payload, movie_id):

        body = request.get_json()

        if not movie_id:
            abort(400, {'message': 'append an movie id to request url'})

        if not body:
            abort(400, {'message': 'reuest doent contain a valid JSON'})

        movie_update = Movie.query.filter(Movie.id == movie_id).one_or_none()

        if not actor_update:
            abort(
                404, {'message': 'Actor with id {} not found in database'
                      .format(actor_id)})

        name = body.get('name', actor_update.name)
        age = body.get('age', actor_update.age)
        gender = body.get('gender', actor_update.gender)

        actor_update.name = name
        actor_update.age = age
        actor_update.gender = gender

        actor_update.update()

        return jsonify({
            'success': True,
            'updated': actor_update.id,
            'actor': [actor_update.format()]
        })

    @app.route('/movies/<movie_id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def delete_movies(payload, movie_id):

        if not movie_id:
            abort(400, {'message': 'append a movie id to the request url'})

        movie_delete = Movie.query.filter(Movie.id == movie_id).one_or_none()

        if not movie_delete:
            abort(
                404, {'message': 'Movie with id {} not found in database'
                      .format(movie_id)})

        movie_delete.delete()

        return jsonify({
            'success': True,
            'deleted': movie_id
        })

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': "bad_request"
        }), 400

    @app.errorhandler(404)
    def resource_not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': "resource not found"
        }), 404

    @app.errorhandler(AuthError)
    def authentification_failed(AuthError):
        return jsonify({
            'success': False,
            'error': AuthError.status_code,
            'message': AuthError.error['description']
        }), AuthError.status_code

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
