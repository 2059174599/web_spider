import json
from collections import defaultdict
import scrapy
import re
import time
import logging
import logging.handlers
# from eversec.settings import Log_file_path
import requests

logger = logging.getLogger('hybrid')


class AnktySpider(scrapy.Spider):
    """
    默认新数据在前页
    """

    name = 'hybrid'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
    }

    def __init__(self):
        self.name = 'hybrid'
        self.start_urls = ['https://www.hybrid-analysis.com/submissions/sandbox/urls', 'https://www.hybrid-analysis.com/submissions/sandbox/files']
        self.page_urls = 'https://shouji.baidu.com/{}'
        self.start_page_url = 1
        self.local_url = 'https://app.eversaas.cn/service/app-ops/gaodeinfo?str={}'
        # 排序
        self.page = None
        self.html_url = 'https://www.hybrid-analysis.com{}'
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
        ids = response.xpath('//ul[@class="pagination"]/li[last()-1]/a/text()').get()
        logger.info('ids:{}'.format(ids))
        if ids:
            ids = int(ids)
        else:
            ids = 1
        ids = self.page if self.page else ids
        for i in range(1, ids+1):
            url = response.url + '?sort=timestamp&sort_order=desc&page={}'.format(i)
            logger.info('列表页url：{}'.format(url))
            yield scrapy.Request(url=url, callback=self.shop_html)

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

    def saveResult(self, path, item):
        with open(path, 'a', encoding='utf-8') as f:
            f.write(item+'\n')

    def shop_html(self, response):

        """
        http://192.168.101.31:8181/docs/app-security/app-security-1ci4upcotsua0
        """
        # from lxml import etree
        # html = etree.HTML(response.text)
        # html_data = html.xpath('//*[@id="submissions-container"]/div[6]/table/tbody/tr[1]/td[5]//text()')
        # print(html_data,'^^^^^^^^^^^^')
        lines = response.xpath('//tbody[@class="rowlink"]/tr')
        print(len(lines),'&&&&&&&&&&')
        for line in lines:
            item = defaultdict(str)
            item['Timestamp'] = line.xpath('./td[1]/text()').get().strip()
            item['Input'] = ''.join(i+'\n' for i in line.xpath('./td[2]//text()').getall() if i.strip())
            item['ThreatLevel'] = line.xpath('./td[3]/span//text()').get().strip() if line.xpath('./td[3]/span//text()') else line.xpath('./td[3]//text()').get().strip()
            item['AnalysisSummary'] = ''.join(i.strip() for i in line.xpath('./td[5]//text()').getall() if i.strip())
            item['Countries'] =  [self.html_url.format(i) for i in line.xpath('./td[6]/span/img/@src').getall() if i]
            item['Environment'] = line.xpath('./td[7]/span/text()').get().strip()
            item['SpiderTime'] = time.strftime("%Y-%m-%d", time.localtime())
            item['Url'] = response.url
            self.saveResult('../log/result_hybrid.json', json.dumps(item, ensure_ascii=False))
