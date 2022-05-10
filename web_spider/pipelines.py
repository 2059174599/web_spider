# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import re
import json
import requests
from eversec.toKafka import KafkaTest
import logging
logger = logging.getLogger(__name__)
import datetime

class EversecPipeline:


    """
    存储
    """
    local_url = 'https://app.eversaas.cn/service/app-ops/gaodeinfo?str={}'
    # kafka_ins = KafkaTest()
    names = ['huya', 'douyu_live']

    def replace_data(self, name):
        """
        替换
        """
        lists = ['更新日期：', '大小：', '版本：']
        for i in lists:
            name = name.replace(i, '')
        return name

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

    def get_md5(self, strs):
        pass

    def get_local(self, item):
        if item['developer']:
            url = self.local_url.format(item['developer'])
            data = requests.get(url).text
            data = json.loads(data)
            if data['body']:
                item['province'] = data['body']['province'] if data['body']['province'] else ''
                item['city'] = data['body']['city'] if data['body']['city'] else ''
            else:
                item['province'] = ''
                item['city'] = ''
        else:
            item['province'] = ''
            item['city'] = ''
        return item

    def saveResult(self, file, result):
        with open(file, 'a', encoding='utf-8') as f:
            f.write(result + '\n')

    def checkItem(self, item):
        keys = ['depth', 'download_timeout', 'download_slot', 'download_latency']
        for i in keys:
            if i in item:
                del item[i]
        return item

    def process_item(self, item, spider):
        item = self.checkItem(item)
        if spider.name in self.names:
            self.saveResult('../result/{}_{}.out'.format(spider.name, datetime.datetime.now().strftime("%Y-%m-%d")), json.dumps(item, ensure_ascii=False))
        else:
            item = self.get_local(item)
            item['apksize'] = self.replace_data(item['apksize'])
            item['updatetime'] = self.replace_data(item['updatetime'])
            item['introduce'] = self.fit_date(item['introduce'])
            item['version'] = self.replace_data(item['version'])
            item['apksize'] = self.unit_conversion(item['apksize'])
            item['dlamount'] = self.unit_conversion(item['dlamount'])
            item['source'] = 'pc'
            print('************', item)
            # self.kafka_ins.async_produce_message(item, topic)
            # del item['introduce']
            logger.info('{}'.format(item))
            return item

