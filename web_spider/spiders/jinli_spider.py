from collections import defaultdict
import scrapy
import re
import time
import logging

logger = logging.getLogger('jinli')


class JinliGameSpider(scrapy.Spider):
    """
    默认新数据在前页
    """

    name = 'jinli_game'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
    }

    def __init__(self):
        self.name = 'jinli_game'
        self.start_urls = ['https://game.gionee.com/Front/Category/index/?cku=158655874_null&action=visit&object=category&intersrc=/']
        self.page_urls = 'https://game.gionee.com/Front/Category/index/?category=100&flag=0&page={}'
        self.start_page_url = 1
        self.local_url = 'https://app.eversaas.cn/service/app-ops/gaodeinfo?str={}'

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)

    def parse(self, response):
        """
        获取页码规则
        """
        # stataus = response.status
        # headers = response.request.headers['User-Agent']
        pages = response.xpath('//div[@class="bd"]/div/a[last()-2]/text()').get()
        logger.info('页码：{}'.format(pages))
        # pages = 2
        for i in range(self.start_page_url, int(pages)+1):
            logger.info('第{}页'.format(i))
            url = self.page_urls.format(i)
            yield scrapy.Request(url=url, callback=self.list_url)

    def list_url(self, response):
        """
        获取详情页url规则
        """
        for url in response.xpath('//a[@class="thumb"]/@href').getall()[:1]:
            logger.info('详情页url：{}'.format(url))
            yield scrapy.Request(url=url, callback=self.shop_html)

    def shop_html(self, response):

        """
        http://192.168.101.31:8181/docs/app-security/app-security-1ci4upcotsua0
        """
        item = defaultdict(str)
        item['name'] = response.xpath('//div[@class="game_intro"]/h4/text()').get()
        item['apksize'] = response.xpath('//p[@class="sum"]/span[2]/text()').get()
        item['downloadUrl'] = response.xpath('//p[@class="btn_area"]/a[2]/@href').get()
        item['version'] = response.xpath('//p[@class="sum"]/span[3]/text()').get()
        item['introduce'] = response.xpath('//div[@id="j_content"]').get()
        item['developer'] = response.xpath('//li[@class="name"]/text()').get()
        item['category'] = '游戏'
        item['updatetime'] = response.xpath('//ul[@class="intro_list"]/li[2]/text()').get()
        item['icon_url'] = response.xpath('//div[@class="game_intro"]/a/img/@src').get()
        # item['sceenshot_url'] = response.xpath('//div[@class="tempWrap"]/ul/li/img/@src').getall()
        item['sceenshot_url'] = re.findall(r'data-original="(.*?)"', response.text)
        item['shop'] = '金立游戏商城'
        item['system'] = 'android'
        item['dlamount'] = 0
        item['url'] = response.url
        item['jsonObject'] = {'time': time.strftime("%Y-%m-%d", time.localtime())}
        logger.info('数据：{}'.format(item['name']))
        yield item