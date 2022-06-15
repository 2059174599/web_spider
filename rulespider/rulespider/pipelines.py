# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
from scrapy.utils.python import to_bytes
from itemadapter import ItemAdapter
import re
import pymongo
import hashlib

class RulespiderPipeline:

    @classmethod
    def from_crawler(cls, crawler):
        """
        读取配置
        """
        cls.mongo_connect = crawler.settings.get('MONGO_URL')
        cls.mongo_database = crawler.settings.get('MONGO_DATABASES')
        cls.mongo_collection = crawler.settings.get('MONGO_COLLECTION')
        return cls()

    def unit_conversion(self, name):
        try:
            if 'MB' in name:
                name = name.replace('MB', '')
                return int(float(name) * 1024 * 1024)
            if 'M' in name:
                name = name.replace('M', '')
                return int(float(name) * 1024 * 1024)
            if '亿' in name:
                name = name.replace('亿', '')
                return int(float(name) * 100000000)
            if '千万' in name:
                name = name.replace('千万', '')
                return int(float(name) * 10000000)
            if '百万' in name:
                name = name.replace('百万', '')
                return int(float(name) * 1000000)
            if '十万' in name:
                name = name.replace('十万', '')
                return int(float(name) * 100000)
            if '万' in name:
                name = name.replace('万', '')
                return int(float(name) * 10000)
        except:
            try:
                return int(name)
            except:
                return 0

    def fit_date(self, name):
        """
        过滤
        """
        dr = re.compile(r'<[^>]+>', re.S)
        name = dr.sub('', name)
        return name.strip()

    def get_result(self, item):
        with open('result.out', 'a', encoding='utf-8') as f:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    def open_spider(self, spider):
        """
        数据库链接
        """
        self.mongo_client = pymongo.MongoClient(self.mongo_connect)
        self.mongo_db = self.mongo_client[self.mongo_database]

    def get_id(self, item, names):
        _id = hashlib.md5(to_bytes(item['version']))
        for name in names:
            _id.update(to_bytes(str(item[name])))
        _id = _id.hexdigest()
        return _id

    def process_item(self, item, spider):
        """
        数据处理
        """
        item['introduce'] = self.fit_date(item['introduce'])
        item['apksize'] = self.unit_conversion(item['apksize'])
        names = ['apksize', 'developer', 'downloadUrl']
        if spider.name == 'jinli':
            names = ['apksize', 'developer']
        _id = self.get_id(item, names)
        self.mongo_db[self.mongo_collection].update_one(
                                {'_id': _id},
                                {'$set': dict(item)},
                                True
                                )

        return item

    def clase_spider(self, spider):
        """
        数据库关闭
        """
        self.mongo_client.close()
