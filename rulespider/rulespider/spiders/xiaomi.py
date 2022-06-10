import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import re

class XiaoMiSpider(CrawlSpider):

    name = 'xiaomi'
    def __init__(self, *args, **kwargs):
        self.allowed_domains = ['ssr1.scrape.center']
        self.base_url = 'https://game.xiaomi.com/api/classify/getCategory?firstCategory=&secondCategory=&apkSizeMin=0&apkSizeMax=0&language=&network=-1&options=&page={}&gameSort=1'
        self.page = 2
        self.start_urls = [self.base_url.format(i) for i in range(1, self.page)]
        # start_urls = ['https://ssr1.scrape.center/']
        self.html_url = 'https://game.xiaomi.com/game/{}'

        super(XiaoMiSpider, self).__init__(*args, **kwargs)

    def process_value(self, value):
        print('&&&&&&&&&&&&', value)
        # for index, link in enumerate(links):
        #     url = self.html_url.format(link)
        #     yield url

    def process_links(self, links):
        for index, link in enumerate(links):
            print('**********:', link)
            yield link

    rules = (
        Rule(LinkExtractor(allow='gameId":\d{8}', process_value='process_value'), follow=True, callback='parse_detail', process_links='process_value'),
    )


    def parse_detail(self, response):
        print('$$$$$$$$$$$$$')
        print(response.url)
        # item = {}
        #item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        #item['name'] = response.xpath('//div[@id="name"]').get()
        #item['description'] = response.xpath('//div[@id="description"]').get()
        # return item
