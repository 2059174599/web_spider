from collections import defaultdict
import scrapy
import re
import time
import logging
import json
import math

logger = logging.getLogger(__name__)


class XiaoMiGameSpider(scrapy.Spider):
    """
    默认新数据在前页
    """

    name = '360_game'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
    }

    def __init__(self):
        self.name = '360'
        self.start_urls = ['http://m.app.so.com/category/request?page=1&requestType=ajax&cid=4']
        self.class_urls = 'http://m.app.so.com/category/cat_request?page=1&requestType=ajax&cid=4&csid={}&order=newest+'
        self.start_page_url = 1
        self.page_urls = 'http://m.app.so.com/category/cat_request?page={}&requestType=ajax&cid=4&csid={}&order=newest+'
        self.page = 21
        self.html_url = 'http://m.app.so.com/detail/index?pname=com.sincetimes.dragonfarmii.qihoo&id={}'

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """
        获取类别规则
        """
        html = response.text
        for i in json.loads(html)[1:]:
            # print(i['total'])
            url = self.class_urls.format(i['category_id'])
            yield scrapy.Request(url=url, callback=self.page_url, meta=i)

    def page_url(self, response):
        """
        获取页码规则
        """
        meta = response.meta
        page = math.ceil(int(meta['total'])/20)
        page = self.page if self.page else page
        logger.info('page:{}'.format(page))
        for i in range(1, page+1):
            url = self.page_urls.format(i, meta['category_id'])
            logger.info('列表页url：{}'.format(url))
            yield scrapy.Request(url=url, callback=self.list_url)

    def list_url(self, response):
        """
        获取列表页规则
        """
        html = response.text
        for date in json.loads(html):
            url = self.html_url.format(date['id'])
            logger.info('详情页url：{}'.format(url))
            yield scrapy.Request(url=url, callback=self.shop_html, meta=date)

    def getRe(self, strs, html):
        try:
            return re.search(strs, html).group(1)
        except:
            return ''

    def shop_html(self, response):

        """
        http://192.168.101.31:8181/docs/app-security/app-security-1ci4upcotsua0
        """
        date = response.meta
        item = defaultdict(str)
        item['name'] = date['name']
        item['apksize'] = response.xpath('/html/body/div[1]/section[1]/div[3]/span[3]/text()').get()
        item['downloadUrl'] = date['down_url']
        item['version'] = date['version_name']
        item['introduce'] = response.xpath('//*[@id="fullDesc"]').get()
        item['developer'] = self.getRe(r'开发者：(.*?)</div>', response.text)
        item['category'] = '游戏'
        item['updatetime'] = self.getRe(r'更新时间：(.*?)</p>', response.text).split(' ')[0]
        item['icon_url'] = date['logo_url']
        # item['sceenshot_url'] = response.xpath('//div[@class="tempWrap"]/ul/li/img/@src').getall()
        item['sceenshot_url'] = response.xpath('//div[contains(@class, "app-image")]/img/@src').getall()
        item['shop'] = '360手机助手'
        item['system'] = 'android'
        item['dlamount'] = date['download_times']
        item['url'] = response.url
        item['jsonObject'] = {'time': time.strftime("%Y-%m-%d", time.localtime())}
        logger.info('数据：{}'.format(item['name']))
        yield item