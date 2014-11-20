from smapp_twitter_admin import app
from bson.objectid import ObjectId
from pymongo import MongoClient
from smapp_toolkit.twitter import MongoTweetCollection
from datetime import datetime, timedelta

_client = MongoClient(app.config['db']['host'], app.config['db'].get('port', 27017))
if 'username' in app.config['db'] and 'password' in app.config['db']:
    _client.admin.authenticate(app.config['db']['username'], app.config['db']['password'])

def _metadata_for(collection_name):
    return _client[collection_name]['smapp_metadata'].find_one({'document': 'smapp-tweet-collection-metadata'})

def _filter_criteria_collection_name(collection_name):
    if 'collection-name-exceptions' in app.config and collection_name in app.config['collection-name-exceptions']:
        return app.config['collection-name-exceptions'][collection_name].get('filter-criteria', 'tweets_filter_criteria')
    return 'tweets_filter_criteria'

def _tweets_collection_name(collection_name):
    if 'collection-name-exceptions' in app.config and collection_name in app.config['collection-name-exceptions']:
        return app.config['collection-name-exceptions'][collection_name].get('tweets', 'tweets')
    return 'tweets'

def _limits_collection_name(collection_name):
    return _tweets_collection_name(collection_name) + '_limits'

class Entity:
    @classmethod
    def all(cls):
        return cls._collection.find({'collection_name' : { '$ne' : 'Permission'}})

    @classmethod
    def find(cls, findby):
        return cls._collection.find({cls._findby: findby})

class Permission(Entity):
    _collection = _client['FilterCriteriaAdmin']['permission']
    _findby = 'collection_name'

    @classmethod
    def collections_for_user(cls, user):
        return [permission['collection_name'] for permission in cls._collection.find({'permitted': {'$in': [user]}})]

class FilterCriteria:
    @classmethod
    def _collection_for(cls, collection_name):
        return _client[collection_name][_filter_criteria_collection_name(collection_name)]

    @classmethod
    def find_by_collection_name(cls, collection_name, query={}):
        return cls._collection_for(collection_name).find(query)

    @classmethod
    def find_by_collection_name_and_object_id(cls, collection_name, id):
        return cls._collection_for(collection_name).find_one({'_id': ObjectId(id)})

    @classmethod
    def update(cls, collection_name, id, data):
        data['_id'] = ObjectId(id)
        return cls._collection_for(collection_name).save(data)

    @classmethod
    def delete(cls, collection_name, id):
        return cls._collection_for(collection_name).remove({'_id': ObjectId(id)})

    @classmethod
    def create(cls, collection_name, data):
        return cls._collection_for(collection_name).save(data)

class PostFilter:
    @classmethod
    def _collection_for(cls, collection_name):
        mongo_col_name = _metadata_for(collection_name).get('post_filters_collection', 'tweets_post_filters')
        return _client[collection_name][mongo_col_name]

    @classmethod
    def count(cls, collection_name):
        return cls._collection_for(collection_name).count()

    @classmethod
    def all_for(cls, collection_name):
        return list(cls._collection_for(collection_name).find())

    @classmethod
    def find_by_collection_name_and_object_id(cls, collection_name, id):
        return cls._collection_for(collection_name).find_one({'_id': ObjectId(id)})

    @classmethod
    def update(cls, collection_name, id, data):
        data['_id'] = ObjectId(id)
        return cls._collection_for(collection_name).save(data)

    @classmethod
    def delete(cls, collection_name, id):
        return cls._collection_for(collection_name).remove({'_id': ObjectId(id)})

    @classmethod
    def create(cls, collection_name, data):
        return cls._collection_for(collection_name).save(data)


class Tweet:
    @classmethod
    def _collection_for(cls, collection_name):
        return MongoTweetCollection(address=app.config['db']['host'], port=app.config['db'].get('port', 27017),
                                    dbname=collection_name, username=app.config['db']['username'],
                                    password=app.config['db']['password'])
    @classmethod
    def count(cls, collection_name):
        return cls._collection_for(collection_name).count()

    @classmethod
    def since(cls, collection_name, since, n=1000):
        return list(cls._collection_for(collection_name).since(since).sort('timestamp',-1).limit(n))

    @classmethod
    def latest(cls, collection_name, n):
        return list(cls._collection_for(collection_name).using_latest_collection_only().sort('timestamp',-1).limit(n))


class LimitMessage:
    @classmethod
    def _collection_for(cls, collection_name):
        return _client[collection_name][_limits_collection_name(collection_name)]

    @classmethod
    def all_for(cls, collection_name):
        return cls._collection_for(collection_name).find().sort('timestamp')