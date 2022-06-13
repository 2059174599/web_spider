# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import re

class RulespiderPipeline:

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

    def process_item(self, item, spider):
        item['introduce'] = self.fit_date(item['introduce'])
        item['apksize'] = self.unit_conversion(item['apksize'])
        print('pipline********', item)

        return item
