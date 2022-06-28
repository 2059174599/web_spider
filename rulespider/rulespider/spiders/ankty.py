from collections import defaultdict
import scrapy
import re
import time
import logging
import logging.handlers
import requests

logger = logging.getLogger(__name__)

class AnktySpider(scrapy.Spider):
    """
    默认新数据在前页
    """

    name = 'anktys'

    def __init__(self):
        self.start_urls = ['https://www.ankty.com/list-61-1-0-1-1.html', 'https://www.ankty.com/list-61-2-0-1-1.html']
        self.page_urls = 'https://shouji.baidu.com/{}'
        self.start_page_url = 1
        self.local_url = 'https://app.eversaas.cn/service/app-ops/gaodeinfo?str={}'
        # 排序
        self.page = 1
        self.html_url = 'https:{}'
        self.down_url = 'https://www.xuanbiaoqing.com/api/show_download_url/{}'

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.page_url)

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
        ids = response.xpath('//div[@class="fenye"]/a[last()-1]/text()').get()
        logger.info('ids:{}'.format(ids))
        if ids:
            ids = int(ids)
        else:
            ids = 1
        ids = self.page if self.page else ids
        for i in range(1, ids+1):
            lists = response.url.split('-')
            lists[-2] = i
            url = '-'.join(str(i) for i in lists)
            logger.info('列表页url：{}'.format(url))
            yield scrapy.Request(url=url, callback=self.list_url, dont_filter=True)

    def list_url(self, response):
        """
        获取列表页规则
        """
        for i in response.xpath('/html/body/div[3]/div/div[1]/div/a/@href').getall():
            url = self.html_url.format(i)
            logger.info('详情页url：{}'.format(url))
            yield scrapy.Request(url=url, callback=self.shop_html)

    def getRe(self, parament, html):
        try:
            res = re.search(parament, html).group(1)
        except Exception as e:
            logging.error('正则：{}, {}'.format(parament, e))
            res = ''
        return res

    def getDown(self, url):
        id = url.split('/')[-1].split('.')[0]
        r = requests.get(self.down_url.format(id), headers=self.headers).text
        downUrl = self.getRe('href="(.*?)"', r)
        return downUrl

    def shop_html(self, response):

        """
        http://192.168.101.31:8181/docs/app-security/app-security-1ci4upcotsua0
        """
        item = defaultdict(str)
        item['name'] = response.xpath('//h1/text()').get().strip()
        item['apksize'] = self.getRe(r'大小：<.*?>(.*?)<', response.text)
        item['downloadUrl'] = self.html_url.format(response.xpath('//div[@class="xzxq_zuo_main_anniu"]/a[1]/@href').get())
        item['version'] = '' #self.getRe(r'版本：</dt><dd>(.*?)</dd', response.text)
        item['introduce'] = response.xpath('//div[@class="xzxq_you_h1_conter"]/p[1]').get()
        item['developer'] = '' #self.getRe(r'厂商：</dt><dd>(.*?)</dd', response.text)
        item['category'] = '游戏'
        item['updatetime'] = self.getRe(r'更新：<i>(.*?)</', response.text).split(' ')[0]
        item['icon_url'] = self.html_url.format(response.xpath('//div[@class="fl"]/img/@src').get())
        # item['sceenshot_url'] = response.xpath('//div[@class="tempWrap"]/ul/li/img/@src').getall()
        item['sceenshot_url'] = [self.html_url.format(i) for i in response.xpath('//div[@class="pic-bd"]/ul/li/div/img/@src').getall()]
        item['shop'] = 'qq下载站'
        item['system'] = 'android'
        item['dlamount'] = 0
        item['url'] = response.url
        item['jsonObject'] = {'time': time.strftime("%Y-%m-%d", time.localtime())}
        logger.info('数据：{}'.format(item['name']))
