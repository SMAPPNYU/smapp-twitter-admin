from smapp_twitter_admin import app
from pymongo import MongoClient

_client = MongoClient(app.config['db']['host'], app.config['db'].get('port', 27017))
if 'username' in app.config['db'] and 'password' in app.config['db']:
    _client.admin.authenticate(app.config['db']['username'], app.config['db']['password'])


class Entity:
    @classmethod
    def all(cls):
        return cls._collection.find()

    @classmethod
    def find(cls, findby):
        return cls._collection.find({cls._findby: findby})

class Permission(Entity):
    _collection = _client['FilterCriteriaAdmin']['permission']
    _findby = 'collection_name'


