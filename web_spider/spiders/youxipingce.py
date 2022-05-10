from collections import defaultdict
import scrapy
import re
import time
import logging
import logging.handlers
# from eversec.settings import Log_file_path
import requests

logger = logging.getLogger('ankty')
# logger.setLevel(level=logging.INFO)
# handler = logging.handlers.RotatingFileHandler(Log_file_path,  mode="a", encoding='utf-8')
# handler.setLevel(logging.INFO)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)

class QqSpider(scrapy.Spider):
    """
    默认新数据在前页
    """

    name = 'qq'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
    }

    def __init__(self):
        self.name = 'qq'
        self.start_urls = ['http://www.gamepingce.com/game/', 'http://www.gamepingce.com/app/']
        self.page_urls = 'https://shouji.baidu.com/{}'
        self.start_page_url = 1
        self.local_url = 'https://app.eversaas.cn/service/app-ops/gaodeinfo?str={}'
        # 排序
        self.page = 2
        self.html_url = 'http://www.gamepingce.com{}'
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
        ids = response.xpath('//div[@class="pagecode"]/a[last()]/@href').get()
        logger.info('ids:{}'.format(ids))
        if ids:
            ids = int(ids.split('_')[-1].strip('/'))
        else:
            ids = 1
        ids = self.page if self.page else ids
        for i in range(1, ids+1):
            url = response.url + 'list_1_{}'.format(i)
            logger.info('列表页url：{}'.format(url))
            yield scrapy.Request(url=url, callback=self.list_url)

    def list_url(self, response):
        """
        获取列表页规则
        """
        for i in response.xpath('//div[@class="tab_box"]/div/div[1]/ul/li/a[1]/@href').getall():
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
        item['apksize'] = self.getRe(r'大小：(.*?)<', response.text)
        item['downloadUrl'] = response.xpath('//*[@id="wangye-yy-btn"]/a/@href').get()
        item['version'] = '' #self.getRe(r'版本：</dt><dd>(.*?)</dd', response.text)
        item['introduce'] = response.xpath('//div[@class="cont"]').get()
        item['developer'] = '' #self.getRe(r'厂商：</dt><dd>(.*?)</dd', response.text)
        item['category'] = '游戏'
        item['updatetime'] = self.getRe(r'更新时间：(.*?)</', response.text)
        item['icon_url'] = 'http://www.gamepingce.com' + response.xpath('/html/body/div[5]/div[1]/div[1]/img/@src').get()
        # item['sceenshot_url'] = response.xpath('//div[@class="tempWrap"]/ul/li/img/@src').getall()
        item['sceenshot_url'] = response.xpath('//*[@id="picScroll"]/ul/li/img/@src').getall()
        item['shop'] = '游戏评测网'
        item['system'] = 'android'
        item['dlamount'] = 0
        item['url'] = response.url
        item['jsonObject'] = {'time': time.strftime("%Y-%m-%d", time.localtime())}
        logger.info('数据：{}'.format(item['name']))
        yield item