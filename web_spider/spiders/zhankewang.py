from collections import defaultdict
import scrapy
import re
import time
import logging
import logging.handlers
# from eversec.settings import Log_file_path
import requests, json
from urllib import parse

logger = logging.getLogger('zahngkewang')
# logger.setLevel(level=logging.INFO)
# handler = logging.handlers.RotatingFileHandler(Log_file_path,  mode="a", encoding='utf-8')
# handler.setLevel(logging.INFO)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)

class XiaoMiGameSpider(scrapy.Spider):
    """
    默认新数据在前页
    """

    name = 'zhankewang'
    def __init__(self):
        self.name = 'zkw'
        # 软件 游戏
        self.start_urls = ['https://www.cncnzz.com/android/azyx', 'https://www.cncnzz.com/android/azrj_id']
        self.page_urls = 'https://shouji.baidu.com/{}'
        self.start_page_url = 1
        self.local_url = 'https://app.eversaas.cn/service/app-ops/gaodeinfo?str={}'
        # 排序
        self.page = 1
        self.down_url = 'https://www.cncnzz.com/getAppDownLink'
        self.headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
         'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36',
        }

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
        ids = response.xpath('//ul[@class="pagingUl"]/a[last()-1]/text()').get()
        logger.info('ids:{}'.format(ids))
        if ids:
            ids = int(ids)
        else:
            ids = 1
        ids = self.page if self.page else ids
        for i in range(1, ids+1):
            url = response.url.strip('/') + '_{}/'.format(i)
            logger.info('列表页url：{}'.format(url))
            yield scrapy.Request(url=url, callback=self.list_url)

    def list_url(self, response):
        """
        获取列表页规则
        """
        for i in response.xpath('//ul[@class="con_list"]/li/a/@href').getall():
            # url = self.html_url.format(i)
            logger.info('详情页url：{}'.format(i))
            yield scrapy.Request(url=i, callback=self.shop_html)

    def getRe(self, parament, html):
        try:
            res = re.search(parament, html).group(1)
        except Exception as e:
            logging.error('正则：{}, {}'.format(parament, e))
            res = ''
        return res

    def getDown(self, url):
        ids = url.split('/')[-1].split('.')[0].split('-')
        data = {
            'downId': ids[1],
            'type': 'PC',
            'key': ids[0],
        }
        r = requests.post(self.down_url, headers=self.headers, data=data).text
        date = json.loads(r)
        name = date['name']
        ids = date['data']['android']['url']
        downUrl = 'https://www.cncnzz.com/dl/{}?from_url=&name={}'.format(ids, name)
        return parse.quote(downUrl)

    def shop_html(self, response):

        """
        http://192.168.101.31:8181/docs/app-security/app-security-1ci4upcotsua0
        """
        item = defaultdict(str)
        item['name'] = response.xpath('//h1/text()').get().strip()
        item['apksize'] = self.getRe(r'大小：</span>(.*?)</li', response.text)
        item['downloadUrl'] = self.getDown(response.url)
        item['version'] = self.getRe(r'版本：</span>(.*?)</li', response.text)
        item['introduce'] = response.xpath('/html/body/main/div/div/div[2]/div[1]/p[1]').get()
        item['developer'] = ''
        item['category'] = '游戏'
        item['updatetime'] = self.getRe(r'更新时间：</span>(.*?)</li', response.text).split(' ')[0]
        item['icon_url'] = response.xpath('//div[@class="soft_wrap clearfix"]/img/@src').get()
        # item['sceenshot_url'] = response.xpath('//div[@class="tempWrap"]/ul/li/img/@src').getall()
        item['sceenshot_url'] = response.xpath('//div[@class="swiper-wrapper"]/div/img/@src').getall()
        item['shop'] = '站客网'
        item['system'] = 'android'
        item['dlamount'] = 0
        item['url'] = response.url
        item['jsonObject'] = {'time': time.strftime("%Y-%m-%d", time.localtime())}
        logger.info('数据：{}'.format(item['name']))
        yield item