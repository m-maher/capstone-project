from datetime import date
from sqlalchemy import desc
from config import bearer_tokens
import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from models import setup_db, db_drop_and_create_all, Actor, Movie, Performance, db_drop_and_create_all

casting_assistant_auth_header = {
    'Authorization': bearer_tokens['casting_assistant']
}

casting_director_auth_header = {
    'Authorization': bearer_tokens['casting_director']
}

executive_producer_auth_header = {
    'Authorization': bearer_tokens['executive_producer']
}


class TestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = os.environ['DATABASE_URL']
        setup_db(self.app, self.database_path)
        db_drop_and_create_all()

        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.create_all()

    def tearDown(self):
        pass

# Tests for actors POST

    def test_create_new_actor(self):
        json_create_actor = {
            'name': 'Crisso',
            'age': 25
        }
        res = self.client().post('/actors', json=json_create_actor,
                                 headers=casting_director_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['created'], 2)

    def test_error_401_new_actor(self):
        json_create_actor = {
            'name': 'Crisso',
            'age': 25
        }
        res = self.client().post('/actors', json=json_create_actor,
                                 headers=casting_director_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Authorization header is expected')

    def test_error_422_create_new_actor(self):
        json_create_actor_without_name = {
            'age': 25
        }
        res = self.client().post('/actors', json=json_create_actor,
                                 headers=casting_director_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'no name provided')

# Tests for actors GET

    def test_get_all_actors(self):
        res = self.client().get('/actors?page=1',
                                headers=casting_assistant_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['actors']) > 0)

    def test_error_401_get_all_actors(self):
        res = self.client().get('/actors?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Authorization header is expected')

    def test_error_404_get_all_actors(self):
        res = self.client().get('/actors?page=123112313',
                                header=casting_assistant_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'no actors found in data base')

# Tests for actors PATCH

    def test_edit_actor(self):
        json_edit_actor_with_new_age = {
            'age': 30
        }
        res = self.client().patch('/actors/1',
                                  json=json_edit_actor_with_new_age,
                                  headers=casting_director_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['actor']) > 0)
        self.assertEqual(data['updated'], 1)

    def test_error_400_edit_actor(self):
        res = self.client().patch('/actors/1324',
                                  headers=casting_director_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(
            data['message'], 'request doesnt contain a valid JSON')

    def test_error_404_edit_actor(self):
        json_edit_actor_with_new_age = {
            'age': 30
        }
        res = self.client().patch('/actors/1324',
                                  json=json_edit_actor_with_new_age,
                                  headers=casting_director_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(
            data['message'], 'Actor with id 1324 not found in database')

# Tests for actors DELETE

    def test_delete_actor(self):
        res = self.client().delete('/actors/1',
                                   headers=casting_director_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], '1')

    def test_error_401_delete_actor(self):
        res = self.client().delete('/actors/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Authorization header is expected')

    def test_error_403_delete_actor(self):
        res = self.client().delete('/actors/1',
                                   headers=casting_assistant_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Permission not found')

    def test_error_404_delete_actor(self):
        res = self.client().delete('/actors/11313',
                                   headers=casting_director_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(
            data['message'], 'Actor with id 11313 not found in database')

# Tests movies POST

    def test_create_new_movie(self):
        json_create_movie = {
            'title': 'Crisso Movie',
            'release_date': date.today()
        }

        res = self.client().post('/movies', json=json_create_movie,
                                 headers=executive_producer_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['created'], 2)

    def test_create_new_movie(self):
        json_create_movie = {
            'release_date': date.today()
        }

        res = self.client().post('/movies',
                                 json=json_create_movie_without_name,
                                 headers=executive_producer_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'no title provided')

# Tests for movies GET

    def test_get_all_movies(self):
        res = self.client().get('/movies?page=1',
                                json=json_create_movie_without_name,
                                headers=executive_producer_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['movies']) > 0)

    def test_error_401_get_all_movies(self):
        res = self.client().get('/movies?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Authorization header is expected')

    def test_error_404_get_all_movies(self):
        res = self.client().get('/movies?page=1323432',
                                headers=casting_assistant_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'no movies found in database')

# Tests for movies PATCH

    def test_edit_movie(self):
        json_edit_movie = {
            'release_date': date.today()
        }
        res = self.client().patch('/movies/1',
                                  json=json_edit_movie,
                                  headers=executive_producer_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['movie']) > 0)

    def test_error_400_edit_movie(self):
        res = self.client().patch('/movies/1',
                                  headers=executive_producer_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'request doent contain a valid JSON')

    def test_error_404_edit_movie(self):
        json_edit_movie = {
            'release_date': date.today()
        }
        res = self.client().patch('/movies/113213',
                                  json=json_edit_movie,
                                  headers=executive_producer_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(
            data['message'], 'Movies with id 113213 not found in database')

# Tests for movies DELETE

    def test_delete_movie(self):
        res = self.client().delete('/movies/1',
                                   headers=executive_producer_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], '1')

    def test_error_401_delete_movie(self):
        res = self.client().delete('/movies/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Authorization header is expected')

    def test_error_403_delete_movie(self):
        res = self.client().delete('/movies/1',
                                   headers=casting_assistant_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Permission not found')

    def test_error_404_delete_movie(self):
        res = self.client().delete('/movies/13332',
                                   headers=executive_producer_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(
            data['message'], 'Movie with id 13332 not found in database.')
