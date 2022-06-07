import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import re

class HuyaSpider(CrawlSpider):

    name = 'xiaomi'

    def __init__(self):
        # self.name = 'xiaomi'
        self.base_url = 'https://game.xiaomi.com/api/classify/getCategory?firstCategory=&secondCategory=&apkSizeMin=0&apkSizeMax=0&language=&network=-1&options=&page={}&gameSort=1'
        self.page = 3
        self.start_urls = [self.base_url.format(i) for i in range(1, self.page)]
        self.html_url = 'https://game.xiaomi.com/game/{}'

    def detail_url(self, value):
        print('&&&&&&&&&&&&&&&&&')
        ids = set(re.findall(r'gameId":(.*?),', value))
        urls = [self.html_url.format(i) for i in ids]
        print('*******', urls)
        return urls
    rules = (
        Rule(LinkExtractor(process_value=), callback='parse_item', follow=True),
    )

    def detail_url(self, value):
        m = set(re.findall(r'gameId":(.*?),', value))

    def parse_item(self, response):
        print(response.url)
        # item = {}
        #item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        #item['name'] = response.xpath('//div[@id="name"]').get()
        #item['description'] = response.xpath('//div[@id="description"]').get()
        # return item
