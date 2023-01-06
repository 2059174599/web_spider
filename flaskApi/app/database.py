import redis
import pymongo
from .config import global_config
from datetime import date, timedelta

class BaseDb(object):
    """
    数据库操作
    """
    def __init__(self):
        self.redis_url = global_config.getRaw('redis', 'REDIS_URL')
        self.redis_clent = redis.from_url(url=self.redis_url, db=global_config.getRaw('redis', 'REDIS_DB'))
        self.redis_key = global_config.get('redis', 'REDIS_KEY')
        self.mongo_client = pymongo.MongoClient(global_config.get('mongo', 'MONGO_URL'))
        database = global_config.get('mongo', 'MONGO_DATABASES')
        self.mongo_db = self.mongo_client[database]
        self.mongo_collection_monitory = global_config.get('mongo', 'MONGO_COLLECTION_MONITORY')
        self.mongo_collection_local = global_config.get('mongo', 'LOCAL_COLLECTION')
        self.mongo_collection = global_config.get('mongo', 'MONGO_COLLECTION')

    def appinfo_seen(self, name, values):
        added = self.redis_clent.sadd(name, values)
        return added == 1


    def insert_mongo(self, item, _id, collection= 'app_info'):
        """
        数据更新：覆盖
        :param item:
        :param _id:
        :param collection:
        :return:
        """
        self.mongo_db[collection].update_one(
                                {'_id': _id},
                                {'$set': item},
                                True
                                )
    def dict_union(self, d1, d2):
        temp = {}
        keys = ['appCrawlerNum', 'appDownloadNum', 'appDownloadSuccessNum', 'appDownloadErrorNum']
        for key in keys:
            temp[key] = sum([d.get(key, 0) for d in (d1, d2)])
        return temp

    def insert_mongos(self, item, _id):
        """
        数据更新：累加
        :param item:
        :param _id:
        :return:
        """
        data = self.mongo_db[self.mongo_collection_monitory].find_one({"_id": _id})
        if data:
            temp = self.dict_union(data, item)
            item.update(temp)
        self.insert_mongo(item, _id, self.mongo_collection_monitory)

    def get_redis_setdiff(self, keys1, keys2):
        sets = self.redis_clent.sdiff(keys1, keys2)
        return sets

    def get_setdiff(self, name, number, area, city, province):
        """
        分区拉取数据
        :param name: 分区名称
        :param number: 数量
        :param area: 区
        :param city: 市
        :param province:省
        :return: set
        """
        number = int(number) if (number and int(number) < 100) else 1
        local_ = set()
        already_ = set()
        datas = None
        if province:
            datas = self.mongo_db[self.mongo_collection_local].find({"province": province}, {'_id': 1})
        if area:
            datas = self.mongo_db[self.mongo_collection_local].find({"area": area}, {'_id': 1})
        if city:
            datas = self.mongo_db[self.mongo_collection_local].find({"city": city}, {'_id': 1})

        if datas:
            for i in datas:
                local_.add(i['_id'])
            for j in self.redis_clent.smembers(name):
                if isinstance(j, bytes):
                    j = j.decode('utf-8')
                already_.add(j)
            res = local_.difference(already_)
        else:
            res = self.get_redis_setdiff(self.redis_key, name)

        return list(res)[:number]


    def get_mongo_data(self, _id, name=None):
        if isinstance(_id, bytes):
            _id = _id.decode('utf-8')
        data = self.mongo_db[self.mongo_collection].find_one({"_id": _id})
        if data and name:
            self.appinfo_seen(name, _id)
        return [data]

    def get_mongo_datas(self, ids, name):
        datas = []
        for _id in ids:
            if isinstance(_id, bytes):
                _id = _id.decode('utf-8')
            data = self.mongo_db[self.mongo_collection].find_one({"_id": _id})
            if data:
                data.pop('_id')
                datas.append(data)
                self.appinfo_seen(name, _id)
        return datas

    def checkData(self, data):
        """
        data['source'] = all
        """
        if 'source' not in data:
            raise ValueError('参数异常')
        if 'startTime' not in data:
            data['startTime'] = (date.today() + timedelta(days=-30)).strftime("%Y-%m-%d")
        if 'endTime' not in data:
            data['endTime'] = (date.today() + timedelta(days=0)).strftime("%Y-%m-%d")
        return data

    def getData(self, data, key='appCrawlerNum'):
        item = dict()
        collections = self.mongo_db[self.mongo_collection_monitory].find({'monitorDate': {'$gte': data['startTime'], '$lte': data['endTime']}})
        for i in collections:
            if key in i:
                if i['monitorDate'] in item:
                    item[i['monitorDate']] += i[key]
                else:
                    item[i['monitorDate']] = i[key]
        return item

    def test(self):
        for i in self.mongo_db[self.mongo_collection_local].find({'province': '河北省'}):
            print(i)

if __name__=="__main__":
    db = BaseDb()
    sets = db.getData()
