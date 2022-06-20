import scrapy
import logging
import redis
from ..settings import REDIS_URL

logger = logging.getLogger(__name__)


class HuaWeiSpider(scrapy.Spider):
    """
    默认新数据在前页
    """

    name = 'huawei_id'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
    }

    def __init__(self):
        # 游戏 应用
        self.uris = ['56a37d6c494545f98aace3da717845b7', 'b2b4752f0a524fe5ad900870f88c11ed']
        self.start_url = 'https://web-drcn.hispace.dbankcloud.cn/uowap/index?method=internal.getTabDetail&serviceType=20&reqPageNum=1&uri={}'
        self.redcline = redis.from_url(REDIS_URL)


    def start_requests(self):
        for uri in self.uris:
            url = self.start_url.format(uri)
            logger.info('start url:{}'.format(url))
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """
        获取类别id
        """
        data = response.json()
        for line in data['tabInfo']:
            for ids in line['tabInfo']:
                tabid = ids['tabId']
                self.redcline.sadd(self.name, tabid)


