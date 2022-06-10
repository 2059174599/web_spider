import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class MovieSpider(CrawlSpider):
    name = 'movie'
    allowed_domains = ['ssr1.scrape.center']
    start_urls = ['http://ssr1.scrape.center/']

    def process_links(self, links):
        for index, link in enumerate(links):
            print('**********:', link)
            yield link
    def process_value(self, value):
        print('&&&&&&&&&&&&', value)

    rules = (
        Rule(LinkExtractor(allow=r'data-v-7f856186="" class="m-b-sm">.*?</h2>', process_value='process_value'), callback='parse_item', process_links='process_links'),
    )

    def parse_item(self, response):
        print(response.url, '$$$$$$$$')
        # item = {}
        #item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        #item['name'] = response.xpath('//div[@id="name"]').get()
        #item['description'] = response.xpath('//div[@id="description"]').get()
        # return item
