from collections import defaultdict
import scrapy
import re
import time
import logging


logger = logging.getLogger(__name__)


class XiaoMiGameSpider(scrapy.Spider):
    """
    默认新数据在前页
    """

    name = 'xiaomi_game'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
    }

    def __init__(self):
        self.name = 'xiaomi'
        self.start_urls = ['https://www.baidu.com/']
        self.page_urls = 'https://game.xiaomi.com/api/classify/getCategory?firstCategory=&secondCategory=&apkSizeMin=0&apkSizeMax=0&language=&network=-1&options=&page={}&gameSort=1'
        self.start_page_url = 3
        self.local_url = 'https://app.eversaas.cn/service/app-ops/gaodeinfo?str={}'
        self.page = 21
        self.html_url = 'https://game.xiaomi.com/game/{}'

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """
        获取页码规则
        """
        for i in range(self.start_page_url, int(self.page)+1):
            logger.info('第{}页'.format(i))
            url = self.page_urls.format(i)
            yield scrapy.Request(url=url, callback=self.list_url)

    def list_url(self, response):
        """
        获取详情页url规则
        """
        ids = set(re.findall(r'gameId":(.*?),', response.text))
        urls = [self.html_url.format(i) for i in ids]
        for url in urls:
            logger.info('详情页url：{}'.format(url))
            yield scrapy.Request(url=url, callback=self.shop_html)

    def getRe(self, strs, html):
        try:
            return re.search(strs, html).group(1)
        except:
            return ''

    def shop_html(self, response):

        """
        http://192.168.101.31:8181/docs/app-security/app-security-1ci4upcotsua0
        """
        item = defaultdict(str)
        sceenshot_html = re.search(r'<div class="current-view__view-wrap">(.*?)<div id="pic_border', response.text).group(1)
        item['name'] = response.xpath('//h1[@class="game-name"]/text()').get().strip()
        item['apksize'] = self.getRe(r'文件大小：(.*?)</span', response.text)
        item['downloadUrl'] = response.xpath('//a[@data-listener="gameDownloadBtn"]/@href').get()
        item['version'] = self.getRe(r'当前版本：(.*?)</span', response.text)
        item['introduce'] = response.xpath('//div[@class="section-game-desc"]/p').get()
        item['developer'] = response.xpath('//div[@class="game-label-block"]/p[last()]/span/text()').get()
        item['category'] = '游戏'
        item['updatetime'] = response.xpath('//div[@class="game-label-block"]/p[1]/span/text()').get()
        item['icon_url'] = response.xpath('//div[@class="game-icon"]/img/@src').get()
        # item['sceenshot_url'] = response.xpath('//div[@class="tempWrap"]/ul/li/img/@src').getall()
        item['sceenshot_url'] = ['https:' + i for i in re.findall(r'src="(.*?)"', sceenshot_html)]
        item['shop'] = '小米游戏商城'
        item['dlamount'] = 0
        item['system'] = 'android'
        item['url'] = response.url
        item['jsonObject'] = {'time': time.strftime("%Y-%m-%d", time.localtime())}
        logger.info('数据：{}'.format(item['name']))
        yield item