import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class HuyaSpider(CrawlSpider):
    name = 'jinli'
    # allowed_domains = ['v.huya.com']
    start_urls = ['https://game.gionee.com/Front/Category/index/?cku=158655874_null&action=visit&object=category&intersrc=/']

    rules = (
        Rule(LinkExtractor(restrict_xpaths='//a[@class="thumb"]'), callback='parse_item', follow=True),
        Rule(LinkExtractor(restrict_xpaths='//div[@class="bd"]/div'), follow=True),
    )

    def parse_item(self, response):
        print(response.url)
        # item = {}
        #item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        #item['name'] = response.xpath('//div[@id="name"]').get()
        #item['description'] = response.xpath('//div[@id="description"]').get()
        # return item
