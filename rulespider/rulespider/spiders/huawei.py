from collections import defaultdict
import scrapy
import re
import time
import logging
import redis
from ..settings import REDIS_URL, POST_URL
from lxml import etree
import requests
import random

logger = logging.getLogger(__name__)


class HuaWeiSpider(scrapy.Spider):
    """
    目前没找到好方法 重写
    """

    name = 'huawei'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
    }

    def __init__(self):
        # 游戏 应用
        self.start_url = 'https://web-drcn.hispace.dbankcloud.cn/uowap/index?method=internal.getTabDetail&serviceType=20&reqPageNum=1&uri={}'
        self.page_urls = 'https://appgallery.huawei.com/app/{}'
        self.start_page_url = 1
        self.down_url = 'https://appgallery.cloud.huawei.com/appdl/{}'
        self.html_url = 'https://web-drcn.hispace.dbankcloud.cn/uowap/index?method=internal.getTabDetail&serviceType=20&reqPageNum={}&uri={}&maxResults=25&zone=&locale=zh'
        self.page_url = 'https://web-drcn.hispace.dbankcloud.cn/uowap/index?method=internal.getTabDetail&serviceType=20&reqPageNum=1&maxResults=25&uri=app%7C{}&shareTo=&currentUrl=https%253A%252F%252Fappgallery.huawei.com%252Fapp%252F{}&accessId=&appid={}&zone=&locale=zh'
        self.redcline = redis.from_url(REDIS_URL)
        self.page = 1
        self.md5Name = 'apkmd5'
        self.id = 'huawei_id'
        self.post_url = POST_URL

    def start_requests(self):
        for tabId in list(self.redcline.smembers(self.id))[:1]:
            tabId = '1a4acc3b50c142e5aab54629d98c90ca'
            url = self.html_url.format(self.page, tabId)
            logger.info('start url:{}'.format(url))
            yield scrapy.Request(url=url, callback=self.parse, meta={'tabId':tabId})

    def backNextPage(self, url):
        r = requests.get(url, headers=self.headers).json()
        return r['layoutData']

    def isExise(self, name, md5):
        res = self.redcline.sismember(name, md5)
        if res == 1:
            return True
        else:
            return False

    def parse(self, response):
        """
        获取类别id
        """
        data = response.json()['layoutData']
        tabId = response.meta['tabId']
        while data:
            for line in data[0]['dataList']:
                if not self.isExise(self.md5Name, line['md5']):
                    item = dict()
                    url = self.page_url.format(line['appid'], line['appid'], line['appid'])
                    page_data = self.shop_html(url)
                    item['name'] = line['name']
                    item['apksize'] = line['fullSize']
                    item['downloadUrl'] = self.down_url.format(line['appid'])
                    item['version'] = line['appVersionName']
                    item['introduce'] = page_data[0]
                    item['developer'] = page_data[1]
                    item['category'] = line['kindName']
                    item['updatetime'] = page_data[2]
                    item['icon_url'] = line['icon']
                    item['sceenshot_url'] = page_data[3]
                    item['shop'] = '华为应用市场'
                    item['system'] = 'android'
                    dlamount = line['downCountDesc'].strip('<').strip('次安装')
                    item['dlamount'] = self.unit_conversion(dlamount)
                    item['url'] = self.page_urls.format(line['appid'])
                    item['jsonObject'] = {'time': time.strftime("%Y-%m-%d", time.localtime()), 'md5': line['md5']}
                    # md5 添加布隆过滤
                    self.redcline.sadd(self.md5Name, line['md5'])
                    item['_id'] = line['md5']
                    # 持久化
                    result = requests.post(self.post_url, json=item).json()
            logger.info('第:{}页'.format(self.page))
            self.page += 1
            url = self.html_url.format(self.page, tabId)
            time.sleep(random.randint(1, 3))
            data = self.backNextPage(url)

    def replace_data(self, name):
        """
        替换
        """
        lists = ['更新日期：', '大小：', '版本：', '次安装']
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

    def shop_html(self, url):

        page_data = self.backNextPage(url)
        for data in page_data:
            if data['layoutName'] == 'detailappintrocard':
                introduce = data['dataList'][0]['appIntro']
            if data['layoutName'] == 'pcappinfocard':
                dataList = data['dataList'][0]
                developer = dataList['developer']
                updatetime = dataList['releaseDate'].replace('/', '-')
            if data['layoutName'] == 'detailscreencard':
                sceenshot_url = data['dataList'][0]['images']
        return [introduce, developer, updatetime, sceenshot_url]
