# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
from scrapy.utils.python import to_bytes
import requests
import re
import hashlib
from rulespider.toKafka import KafkaTest
import redis
import logging
logger = logging.getLogger(__name__)

class RulespiderPipeline:

    @classmethod
    def from_crawler(cls, crawler):
        """
        读取配置
        """
        cls.post_url = crawler.settings.get('POST_URL')
        cls.fit_names = crawler.settings.get('FIT_NAMES')
        cls.topic = crawler.settings.get('TOPIC')
        cls.redis_url = crawler.settings.get('REDIS_URL')
        cls.redis_key = crawler.settings.get('REDIS_KEY')
        cls.kafka_ins = KafkaTest()
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
            return int(name)
        except:
            try:
                return int(name)
            except:
                return 0
    def replace_data(self, name):
        """
        替换
        """
        lists = ['更新日期：', '大小：', '版本：']
        for i in lists:
            name = name.replace(i, '')
        return name

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
        # self.mongo_client = pymongo.MongoClient(self.mongo_connect)
        self.redis_clent = redis.from_url(self.redis_url)

    def appinfo_seen(self, name, values):
        added = self.redis_clent.sadd(name, values)
        return added == 1

    def get_id(self, item, names):
        _id = hashlib.md5(to_bytes(item['version']))
        for name in names:
            _id.update(to_bytes(str(item[name])))
        _id = _id.hexdigest()
        return _id

    def request_wuhan(self, item):
        """
        发送武汉
        """
        result = requests.post(self.post_url, json=item).json()
        if result['code'] == 200:
            logger.info('武汉请求成功:{}'.format(result))
        else:
            logger.error('武汉请求异常：{}'.format(result))

    def process_item(self, item, spider):
        """
        数据处理
        """
        if spider.name == 'wuhan':
            # 发送kafka
            self.kafka_ins.async_produce_message(dict(item), self.topic)
            return item
        item['updatetime'] = self.replace_data(item['updatetime'])
        item['apksize'] = self.replace_data(item['apksize'])
        item['version'] = self.replace_data(item['version'])
        item['introduce'] = self.fit_date(item['introduce'])
        item['apksize'] = self.unit_conversion(item['apksize'])
        item['source'] = self.redis_key
        configs = ['jinli', 'jinli_test']
        if spider.name in configs:
            self.fit_names = ['apksize', 'developer']
        _id = self.get_id(item, self.fit_names)
        # 是否缓存过
        seen = self.appinfo_seen(self.redis_key, _id)

        if seen:
            # 发送kafka
            self.kafka_ins.async_produce_message(dict(item), self.topic)
            # 传输到武汉
            item['_id'] = _id
            self.request_wuhan(dict(item))

            return item

    def clase_spider(self, spider):
        """
        数据库关闭
        """
        # self.mongo_client.close()
        pass