from flask import current_app
import redis
import pymongo
# from ..settings import REDIS_URL, MONGO_URL, MONGO_DATABASES, MONGO_COLLECTION, REDIS_KEY, REDIS_DB
REDIS_URL = 'redis://:eversec123098@10.0.4.38:6379'
REDIS_DB = 6
REDIS_KEY = 'app_info'
MONGO_URL = 'mongodb://root:eversec123098@10.0.4.38:27001'
MONGO_DATABASES = 'test'
MONGO_COLLECTION = 'app_info'
MONGO_COLLECTION_MONITORY = 'monitory'
class BaseDb(object):
    """
    数据库操作
    """
    def __init__(self):
        self.redis_clent = redis.from_url(url=REDIS_URL, db=REDIS_DB)
        self.redis_key = REDIS_KEY
        self.mongo_client = pymongo.MongoClient(MONGO_URL)
        self.mongo_db = self.mongo_client[MONGO_DATABASES]

    def appinfo_seen(self, name, values):
        added = self.redis_clent.sadd(name, values)
        return added == 1


    def insert_mongo(self, item, _id):
        self.mongo_db[MONGO_COLLECTION].update_one(
                                {'_id': _id},
                                {'$set': item},
                                True
                                )
    def insert_mongos(self, item, _id):
        self.mongo_db[MONGO_COLLECTION_MONITORY].update_one(
                                {'_id': _id},
                                {'$set': item},
                                True
                                )
    def get_setdiff(self, keys1, keys2):
        sets = self.redis_clent.sdiff(keys1, keys2)
        return sets

    def get_mongo_data(self, _id, name):
        if isinstance(_id, bytes):
            _id = _id.decode('utf-8')
        data = self.mongo_db[MONGO_COLLECTION].find_one({"_id": _id})
        if data:
            self.appinfo_seen(name, _id)
        return [data]

    def get_mongo_datas(self, ids, number, name):
        datas = []
        for _id in ids:
            if isinstance(_id, bytes):
                _id = _id.decode('utf-8')
            data = self.mongo_db[MONGO_COLLECTION].find_one({"_id": _id})
            if data:
                data.pop('_id')
                datas.append(data)
                self.appinfo_seen(name, _id)
            if len(datas) >= number:
                break
        return datas

if __name__=="__main__":
    db = BaseDb()
    sets = db.get_setdiff('app_info', 'beijing')
    print('sets:', sets)

    data = db.get_mongo_datas(sets, 2, 'beijing')
    print(data)