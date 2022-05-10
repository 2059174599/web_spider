from collections import defaultdict
import scrapy
import re
import time
import logging
import logging.handlers

logger = logging.getLogger(__name__)


class XiaoMiGameSpider(scrapy.Spider):
    """
    默认新数据在前页
    """

    name = 'baidu_game'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
    }
    def __init__(self):
        self.start_urls = ['https://shouji.baidu.com/game/']
        self.page_urls = 'https://shouji.baidu.com/{}'
        self.start_page_url = 1
        self.local_url = 'https://app.eversaas.cn/service/app-ops/gaodeinfo?str={}'
        self.page = 2
        self.html_url = 'https://shouji.baidu.com/{}'

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """
        获取类别规则
        """
        for i in response.xpath('//*[@id="doc"]/ul/li/div/a/@href').getall():
            # logger.info('第{}页'.format(i))
            url = self.page_urls.format(i)
            yield scrapy.Request(url=url, callback=self.page_url)

    def page_url(self, response):
        """
        获取页码规则
        """
        ids = response.xpath('//div[@class="pager"]/ul/li[last()-1]/a/text()').get()
        if ids:
            ids = int(ids)
        else:
            ids = 1
        ids = self.page if self.page else ids
        for i in range(1, ids+1):
            url = response.url + 'list_{}.html'.format(i)
            logger.info('列表页url：{}'.format(url))
            yield scrapy.Request(url=url, callback=self.list_url, dont_filter=True)

    def list_url(self, response):
        """
        获取列表页规则
        """
        for i in response.xpath('//div[@class="app-bd"]/ul/li/a/@href').getall():
            url = self.html_url.format(i)
            logger.info('详情页url：{}'.format(url))
            yield scrapy.Request(url=url, callback=self.shop_html)

    def shop_html(self, response):

        """
        http://192.168.101.31:8181/docs/app-security/app-security-1ci4upcotsua0
        """
        item = defaultdict(str)
        item['name'] = response.xpath('//h1/span/text()').get().strip()
        item['apksize'] = re.search(r'大小:(.*?)</span', response.text).group(1)
        item['downloadUrl'] = response.xpath('//div[@class="area-download"]/a/@href').get()
        item['version'] = re.search(r'版本:(.*?)</span', response.text).group(1)
        item['introduce'] = response.xpath('//p[contains(@class,"content")]/text()').get()
        item['developer'] = ''
        item['category'] = '游戏'
        item['updatetime'] = ''
        item['icon_url'] = response.xpath('//div[@class="app-pic"]/img/@src').get()
        # item['sceenshot_url'] = response.xpath('//div[@class="tempWrap"]/ul/li/img/@src').getall()
        item['sceenshot_url'] = response.xpath('//div[@class="section-body"]/div/ul/li/img/@src').getall()
        item['shop'] = '百度手机助手'
        item['system'] = 'android'
        item['dlamount'] = re.search(r'下载次数:(.*?)</span', response.text).group(1).strip()
        item['url'] = response.url
        item['jsonObject'] = {'time': time.strftime("%Y-%m-%d", time.localtime())}
        logger.info('数据：{}'.format(item['name']))
        yield item