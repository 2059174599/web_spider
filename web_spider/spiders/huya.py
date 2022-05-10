import json
import logging
import re
import time
import scrapy

from eversec.items import HuyaItem

logger = logging.getLogger(__name__)

class BookSpider(scrapy.Spider):
    name = 'huya'
    start_url = ['https://v.huya.com/g/all?set_id=0']
    type_url = 'https://v.huya.com/g/all_hot_{}'
    page_url = 'https://v.huya.com/g/all?set_id={}&order=new&page={}'
    detail_url = 'https://liveapi.huya.com/moment/getMomentContent?videoId={}'
    author_url = 'https://v.huya.com/u/{}'
    url = 'https://v.huya.com/play/{}.html'
    page = 1

    def start_requests(self):
        for url in self.start_url:
            yield scrapy.Request(url, callback=self.parse_index)

    def parse_index(self, response):
        ids = response.xpath('//div[@class="vhy-list-category-list"]/a[position()>1]/@href').getall()
        types = response.xpath('//div[@class="vhy-list-category-list"]/a[position()>1]/text()').getall()
        # print(ids, types)
        data = dict(zip(ids, types))
        # print('********',data)
        for id in data:
            item = dict()
            item['type'] = data[id]
            id = id.split('=')[-1]
            url = self.type_url.format(id)
            logger.info('TagUrl:{}'.format(url))
            item['typeId'] = id
            yield scrapy.Request(url, callback=self.parse_page, dont_filter=True, meta=item, priority=1)

    def parse_page(self, response):
        item = response.meta
        page = int(response.xpath('//div[@class="pagination"]/a[last()-1]/text()').get())
        page = page if not self.page else self.page
        for i in range(1, page+1):
            url = self.page_url.format(item['typeId'], i)
            logger.info('pageUrl:{}'.format(url))
            yield scrapy.Request(url, callback=self.parse_detail, meta=item, priority=2)

    def parse_detail(self, response):
        item = response.meta
        urls = response.xpath('//section[@class="mod-wrap"]/ul[2]/li/a/@href').getall()
        for url in urls:
            id = re.search('(\d+)', url).group(1)
            item['id'] = id
            item['url'] = self.url.format(id)
            url = self.detail_url.format(id)
            logger.info('detailUrl:{}'.format(url))
            yield scrapy.Request(url, callback=self.parse_videoId, meta=item, priority=5)

    def parse_videoId(self, response):
        item1 = response.meta
        item = HuyaItem()
        data = json.loads(response.text)['data']['moment']
        item['type'] = item1['type']
        item['typeId'] = item1['typeId']
        item['url'] = item1['url']
        item['title'] = data['title']
        item['pubdate'] = data['videoInfo']['videoUploadTime']
        item['favorCount'] = data['favorCount']
        item['comments'] = data['commentCount']
        item['author'] = data['nickName']
        item['authorId'] = data['uid']
        item['videoPlayNum'] = data['videoInfo']['videoPlayNum']
        url = self.author_url.format(data['uid'])
        yield scrapy.Request(url, callback=self.parse_author, meta=item, priority=8)

    def parse_author(self, response):
        item = response.meta
        item['fans'] = response.xpath('//div[@class="detail-info"]/span[1]/em/text()').get()
        item['products'] = response.xpath('//div[@class="detail-info"]/span[2]/em/text()').get()
        item['source'] = '虎牙'
        item['spiderTime'] = time.strftime("%Y-%m-%d", time.localtime())
        logger.info('result:{}'.format(item))
        yield item
