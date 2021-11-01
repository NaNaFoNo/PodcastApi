from enum import _auto_null
import random
import sys
import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.base import NOT_EXTENSION
from sqlalchemy.sql.expression import false
from sqlalchemy.sql.sqltypes import Integer

sys.path.insert(0, '..') # change path to import from parent dir

from app import create_app
from models import test_setup_db, Podcast, Speaker, Episode
from tests.sample import reset_db_tables

"""
Class for Test Cases
"""


class CapstoneTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = os.environ["TEST_DATABASE_URL"]
        self.db = SQLAlchemy()
        test_setup_db(self.app, self.database_path)
        query = Podcast.query.all()
        if not query:
            reset_db_tables(self.app)

        self.new_podcast = {
            'author': 'Test author',
            'name': 'Test Name',
            'image': 'image link',
            'podcast_link': 'podcast link'    
        }

        self.search_podcast = {
            'search': 'Robert'
        }

        self.new_speaker = {
            'name': 'Test Name',
            'image_link': 'image link',
            'twitter_link': 'podcast link',
            'website_link': 'weblink'    
        }

        self.search_speaker = {
            'search': 'Michael'
        }

        podcast_query = Podcast.query.first()
        speaker_query = Speaker.query.first()

        self.new_episode = {
            'title': 'Test Name',
            'topics': 'Tets topic',
            'podcast_link': 'podcast link',
            'speaker_id': speaker_query.id,
            'podcast_id': podcast_query.id 
        }

        self.search_episode = {
            'search': 'Bitcoin'
        }            
    
    def tearDown(self):
        # Executed after reach test
        pass


    """
    Tests
    """
    # Server status
    def test_get_server_status(self):
        res = self.client().get('/')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Healthy')


    # GET Database table Endpoints
    def table_data_tests(self, endpoint, response_data):
        res = self.client().get(endpoint)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(len(data[response_data]), 0)


    def test_get_podcasts(self):
        self.table_data_tests('/podcasts', 'podcasts')

    def test_get_speakers(self):
        self.table_data_tests('/speakers', 'speakers')

    def test_get_episodes(self):
        self.table_data_tests('/episodes', 'episodes')


    # GET id Endpoints + not found
    def test_get_podcast_id(self):
        query = Podcast.query.first()

        res = self.client().get('/podcasts/{}'.format(query.id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['podcasts']['name'], query.name)

    
    def test_get_speaker_id(self):
        query = Speaker.query.first()

        res = self.client().get('/speakers/{}'.format(query.id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['speakers']['name'], query.name)


    def test_get_episode_id(self):
        query = Episode.query.first()

        res = self.client().get('/episodes/{}'.format(query.id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['episodes']['topics'], query.topics)

    
    def not_found_tests(self, endpoint, false_id):
        res = self.client().get('{}/{}'.format(endpoint, false_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    def test_get_podcast_id_not_found(self):
        self.not_found_tests('/podcasts', 12345)

    def test_get_speaker_id_not_found(self):
        self.not_found_tests('/speakers', 12345)

    def test_get_episode_id_not_found(self):
        self.not_found_tests('/episodes', 12345)


        
    # POST endpoints add data

    def create_and_test (self, endpoint, response_values, test_data):
        res = self.client().post(endpoint, json=test_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        for value in test_data:
            self.assertEqual(
                data[response_values][value],
                test_data[value]
            )


    def test_create_new_podcast(self):
        self.create_and_test('/podcasts', 'podcast', self.new_podcast)
    

    def test_create_new_speaker(self):
        self.create_and_test('/speakers', 'speaker', self.new_speaker)
       

    def test_create_new_episode(self):
        self.create_and_test('/episodes', 'episode', self.new_episode)


    # POST endpoints search data

    def search_and_test (self, endpoint, search_value):
        res = self.client().post(endpoint, json=search_value)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
    

    def test_search_podcast(self):
        self.search_and_test('/podcasts', self.search_podcast)
    
    def test_search_speaker(self):
        self.search_and_test('/speakers', self.search_speaker)

    def test_search_episode(self):
        self.search_and_test('/episodes', self.search_episode)

    # PATCH Endpoints
    def update_id_tests(self,endpoint, update_id, update_data, reponse_data):
        res = self.client().patch('{}/{}'.format(endpoint, update_id), json=update_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        for value in update_data:
            self.assertEqual(
                data[reponse_data][value],
                update_data[value]
            )
        
    def test_update_podcast(self):
        search = Podcast.query.first()
        update = {
            'author': search.author,
            'name': search.name,
            'image': search.image_link,
            'podcast_link': str(random.random()) 
        }
        self.update_id_tests('/podcasts', search.id, update, 'podcast')
  
        
    def test_update_speaker(self):
        search = Speaker.query.first()
        update = {
            'name': search.name,
            'image_link': search.image_link,
            'twitter_link': search.twitter_link,
            'website_link': str(random.random())
        }
        self.update_id_tests('/speakers', search.id, update, 'speaker')

    def test_update_episode(self):
        search = Episode.query.first()
        update = {
            'title': search.title,
            'topics': search.topics,
            'podcast_link': str(random.random()),
            'speaker_id': search.speaker_id,
            'podcast_id': search.podcast_id 
        }
        self.update_id_tests('/episodes', search.id, update, 'episode')


        
    # DELETE Endpoints

    def delete_id_tests(self, delete_id, endpoint):
        res = self.client().delete('{}/{}'.format(endpoint, delete_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted_id'], delete_id)
    

    def test_delete_episode(self):
        query = (
            Episode.query
            .filter(Episode.title == self.new_episode['title'])
            .one_or_none()
        )
        self.delete_id_tests(query.id, '/episodes')


    def test_delete_podcast(self):
        query = (
            Podcast.query
            .filter(Podcast.author == self.new_podcast['author'])
            .one_or_none()
        )
        self.delete_id_tests(query.id, '/podcasts')
    
    def test_delete_speaker(self):
        query = (
            Speaker.query
            .filter(Speaker.name == self.new_speaker['name'])
            .one_or_none()
        )
        self.delete_id_tests(query.id, '/speakers')

    def delete_id_not_found_tests(self, endpoint, false_id):
        res = self.client().delete('{}/{}'.format(endpoint, false_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

     
    def test_delete_podcast_not_found(self):
        self.delete_id_not_found_tests('/podcasts', 12345)

    def test_delete_speaker_not_found(self):
        self.delete_id_not_found_tests('/speakers', 12345)
    
    def test_delete_episode_not_found(self):
        self.delete_id_not_found_tests('/episodes', 12345)



if __name__ == "__main__":
    unittest.main()