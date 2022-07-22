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

    name = 'baidu'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
    }
    def __init__(self):
        self.start_urls = ['https://appc.baidu.com/marvel/board/game-types', 'https://appc.baidu.com/marvel/board/app-types']
        self.page_urls = 'https://appc.baidu.com/marvel/board/detail/{}?pn={}&ps=10'
        self.start_page_url = 1
        self.local_url = 'https://app.eversaas.cn/service/app-ops/gaodeinfo?str={}'
        self.page = 2
        self.html_url = 'https://appc.baidu.com/marvel/app-detail/{}'

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """
        获取类别规则
        """
        data = response.json()['data']
        for i in data:
            for page in range(self.page):
                item = dict()
                item['type'] = i['name']
                url = self.page_urls.format(i['boardId'], page)
                yield scrapy.Request(url=url, callback=self.list_url, meta=item)

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
        item = response.meta
        data = response.json()['data']['boards']
        if data[0]['items']:
            for i in data[0]['items']:
                url = self.html_url.format(i['docId'])
                item['apksize'] = i['sizeB']
                logger.info('详情页url：{}'.format(url))
                yield scrapy.Request(url=url, callback=self.shop_html, meta=item)

    def shop_html(self, response):

        """
        http://192.168.101.31:8181/docs/app-security/app-security-1ci4upcotsua0
        """
        i = response.meta
        data = response.json()['data']['info']
        item = defaultdict(str)
        item['name'] = data['title']
        item['apksize'] = i['apksize']
        item['downloadUrl'] = data['downloadInner']
        item['version'] = data['versionName']
        item['introduce'] = data['brief']
        item['developer'] = data['developerName']
        item['category'] = i['type']
        item['updatetime'] = data['updatetime'].split()[0]
        item['icon_url'] = data['icon']
        # item['sceenshot_url'] = response.xpath('//div[@class="tempWrap"]/ul/li/img/@src').getall()
        item['sceenshot_url'] = data['screenshots']
        item['shop'] = '百度手机助手'
        item['system'] = 'android'
        item['dlamount'] = data['allDownload']
        item['url'] = response.url
        item['jsonObject'] = {'time': time.strftime("%Y-%m-%d", time.localtime())}
        logger.info('数据：{}'.format(item['name']))
        yield item