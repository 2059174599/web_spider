import json
import logging
import re
import time
import scrapy

from eversec.items import DouyuItem

logger = logging.getLogger(__name__)

class BookSpider(scrapy.Spider):
    name = 'douyu'
    start_url = ['https://v.douyu.com/']
    page_url = 'https://v.douyu.com/video/videotag/getVideoListByTag?tagId={}&filterTagId=0&cid2=0&page=1&size=20&sort=1&srcTag2=0&isHideReplay=0'
    next_page_url = 'https://v.douyu.com/video/videotag/getVideoListByTag?tagId={}&filterTagId=0&cid2=0&page={}&size=20&sort=1&srcTag2=0&isHideReplay=0'
    detail_url = 'https://v.douyu.com/show/{}'
    comment_url = 'https://yuba.douyu.com/wbapi/video/hotcomment/{}'
    barrage_url = 'https://v.douyu.com/wgapi/vod/center/getBarrageList?vid=Yo4evyKomkxM8L62&start_time=0&end_time=-1'
    play_url = 'https://v.douyu.com/wgapi/vod/center/getShowReplayList?vid=yVmjvB5ryPAWqkNb&up_id=qy70jo1xgdXG'
    url = 'https://v.douyu.com/show/{}'
    author_url = 'https://v.douyu.com/author/{}'
    page = 3

    def start_requests(self):
        for url in self.start_url:
            yield scrapy.Request(url, callback=self.parse_index)

    def parse_index(self, response):
        tagId = response.xpath('//demand-floor-list/demand-floor-mod/@id').getall()
        types = response.xpath('//demand-floor-list/demand-floor-mod//label/text()').getall()
        logger.info('tagId:{}'.format(tagId))
        ids = [tag.split('_')[-1] for tag in tagId]
        data = dict(zip(ids, types))
        logger.info('data:{}'.format(data))
        for id in data:
            item = dict()
            url = self.page_url.format(id)
            logger.info('TagUrl:{}'.format(url))
            item['typeId'] = id
            item['type'] = data[id]
            yield scrapy.Request(url, callback=self.parse_page, meta=item, priority=2)

    def parse_page(self, response):
        item = response.meta
        data = json.loads(response.text)['data']
        page = data['pageCount'] if not self.page else self.page
        for i in range(1, page+1):
            url = self.next_page_url.format(item['typeId'], i)
            logger.info('pageUrl:{}'.format(url))
            yield scrapy.Request(url, callback=self.parse_detail, meta=item, priority=3)

    def parse_detail(self, response):
        item = response.meta
        data = json.loads(response.text)['data']
        for i in data['videoList']:
            item['hashVid'] = i['hashVid']
            url = self.detail_url.format(i['hashVid'])
            logger.info('detailUrl:{}'.format(url))
            yield scrapy.Request(url, callback=self.parse_videoId, priority=5, meta=item)

    def parse_videoId(self, response):
        item1 = response.meta
        item = DouyuItem()
        html = re.search('content:(.*?),videoTag', response.text).group(1)
        data = json.loads(html)
        item['title'] = re.search('<title>(.*?)</title>', response.text).group(1)
        item['pubdate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['update_time']))
        item['type'] = item1['type']
        item['typeId'] = item1['typeId']
        item['url'] = self.url.format(item1['hashVid'])
        item['hashVid'] = item1['hashVid']
        item['favorCount'] = data['likeNum']
        item['share'] = data['share']
        item['author'] = re.search('author_name":"(.*?)"', response.text).group(1).encode('utf-8').decode('unicode_escape')
        item['authorId'] = data['up_id']
        item['videoPlayNum'] = data['view_num']
        url = self.author_url.format(data['up_id'])
        yield scrapy.Request(url, callback=self.parse_author, meta=item, priority=8)

    def parse_author(self, response):
        item = response.meta
        item['fans'] = re.search('subscribeNum:"(.*?)"', response.text).group(1)
        item['products'] = re.search('userVideoCount:"(.*?)"', response.text).group(1)
        item['source'] = '斗鱼'
        item['spiderTime'] = time.strftime("%Y-%m-%d", time.localtime())
        logger.info('result:{}'.format(item))
        url = self.comment_url.format(item['hashVid'])
        yield scrapy.Request(url, callback=self.parse_comment, meta=item, priority=10)

    def parse_comment(self, response):
        item = response.meta
        data = json.loads(response.text)['data']
        item['comments'] = data['total']
        # print(item)
        yield item