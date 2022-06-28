import scrapy


class ShuqiSpider(scrapy.Spider):
    name = 'shuqi'
    # allowed_domains = ['https://www.shuqi.com']
    start_urls = ['https://www.shuqi.com/store/']
    base_url = 'https://www.shuqi.com'
    page = 1

    def parse(self, response):
        type_urls = response.xpath('/html/body/div[1]/div[3]/div[2]/div[2]/ul/li/a/@href').extract()
        type_urls = [self.base_url + i for i in type_urls]
        for url in type_urls:
            yield scrapy.Request(url=url, callback=self.get_page_url)

    def get_page_url(self, response):
        page = response.xpath('//div[@class="comp-web-pages"]/span[last()-2]/a/text()').extract_first()
        page = int(page) if not self.page else self.page
        for i in range(1, page+1):
            url = '{}&page={}'.format(response.url, i)
            yield scrapy.Request(url=url, callback=self.get_book_url)

    def get_book_url(self, response):
        urls = response.xpath('//ul[@class="store-ul clear"]/li/a/@href').extract()
        urls = [self.base_url + i for i in urls]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.get_result)

    def get_result(self, response):
        item = dict()
        item['name'] = response.xpath('//span[@class="bname"]/text()').extract_first()
        item['tags'] = response.xpath('//ul[@class="tags clear"]/li/a/text()').extract()
        item['introduce'] = response.xpath('//p[@class="bookDesc"]//text()').extract_first()
        item['author'] = response.xpath('//span[@class="bauthor"]/a/text()').extract_first()
        item['id'] = response.url.strip('.html').strip('ps://www.shuqi.com/book/')
        item['url'] = response.url
        yield item