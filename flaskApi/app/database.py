from flask import current_app
import redis
import pymongo
from settings import REDIS_URL, MONGO_URL, MONGO_DATABASES, MONGO_COLLECTION, REDIS_KEY

class BaseDb(object):
    """
    数据库操作
    """
    def __init__(self):
        self.redis_clent = redis.from_url(REDIS_URL)
        self.redis_key = REDIS_KEY
        self.mongo_client = pymongo.MongoClient(MONGO_URL)
        self.mongo_db = self.mongo_client[MONGO_DATABASES]

    def appinfo_seen(self, values):
        added = self.redis_clent.sadd(self.redis_key, values)
        return added == 1


    def insert_mongo(self, item, _id):
        self.mongo_db[MONGO_COLLECTION].update_one(
                                {'_id': _id},
                                {'$set': item},
                                True
                                )
    def get_setdiff(self, keys1,keys2):
        sets = self.redis_clent.sdiff(keys1, keys2)
        return sets

    def get_mongo_data(self, _id):
        return [self.mongo_db[MONGO_COLLECTION].find({"_id": _id})]

    def get_mongo_datas(self, ids):
        data = []
        for _id in ids:
            data.append(self.mongo_db[MONGO_COLLECTION].find({"_id": _id}))
        return data
