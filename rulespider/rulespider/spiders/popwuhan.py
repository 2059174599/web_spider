import scrapy
import logging
logger = logging.getLogger(__name__)

class PopwuhanSpider(scrapy.Spider):
    name = 'wuhan'
    allowed_domains = ['58.49.62.62:58090']
    start_urls = ['http://58.49.62.62:58090/db/popAppData?name=wuhan&number=2']


    def parse(self, response):
        for item in response.json()['data']:
            yield item