from collections import defaultdict
import scrapy
import re
import time
import logging
import logging.handlers
from eversec.settings import DATABASE, APK_DOEN
import requests
from lxml import etree
import time
import redis
import hashlib
import json
import os

logger = logging.getLogger(__name__)

class BrowseSpider(object):
    """
    默认新数据在前页
    """

    name = 'browse'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
    }

    def __init__(self):
        self.name = 'browse'
        self.start_urls = ['https://urlhaus.abuse.ch/browse/']
        self.page_urls = 'https://urlhaus.abuse.ch/browse/page/{}/'
        self.start_page_url = 1
        self.local_url = 'https://app.eversaas.cn/service/app-ops/gaodeinfo?str={}'
        self.page = 1
        self.html_url = 'https://urlhaus.abuse.ch{}'
        self.redis_downurl = redis.Redis(**DATABASE['redis_down'])
        self.redis_res = redis.Redis(**DATABASE['redis_res'])
        self.headsers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                         'Accept-Encoding': 'gzip, deflate, br',
                         'Accept-Language': 'zh-CN,zh;q=0.9',
                         'Cache-Control': 'max-age=0',
                         'Connection': 'keep-alive',
                         'Cookie': 'xz_id=a6980754-ed13-32dd-6c58-560d2810176d; Hm_lvt_ececf7308171f13183ebbe384c270488=1638327072; _ga=GA1.2.1999067037.1638327072; Hm_lvt_bdf5c75d42b7a4bcd26762a4a8fd6f93=1638327073; Hm_lvt_1057fce5375b76705b65338cc0397720=1647508088; Hm_lvt_c5d39e518713a0233d647950271d1977=1647508094; HWWAFSESID=d20847387c49f99251; HWWAFSESTIME=1647508097990; Hm_lvt_222aa1e9ba6c9f55f27aea53c8ca28ea=1647508106; Hm_lvt_faba0945fe0cbd52843daca60f70d7a1=1647508564; _gid=GA1.2.2010517075.1647828706; Qs_lvt_67987=1638327072%2C1647508088%2C1647828706; Hm_lpvt_faba0945fe0cbd52843daca60f70d7a1=1647848557; Hm_lpvt_222aa1e9ba6c9f55f27aea53c8ca28ea=1647848575; Hm_lpvt_1057fce5375b76705b65338cc0397720=1647850357; Hm_lpvt_c5d39e518713a0233d647950271d1977=1647850357; Qs_pv_67987=4334963865540246000%2C662158943121773600%2C3313023301123280400%2C3158546710676188000%2C692966999072189600',
                         'Host': 'www.onlinedown.net',
                         'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
                         'sec-ch-ua-mobile': '?0',
                         'sec-ch-ua-platform': '"Windows"',
                         'Sec-Fetch-Dest': 'document',
                         'Sec-Fetch-Mode': 'navigate',
                         'Sec-Fetch-Site': 'none',
                         'Sec-Fetch-User': '?1', 'Upgrade-Insecure-Requests': '1',
                         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'}

    def getRequest(self, url):
        r = requests.get(url, headers = self.headers)
        r.encoding = 'utf-8'
        time.sleep(3)
        return r.text

    def getMd5(self, strs):
        """
        获取MD5
        """
        md5 = hashlib.md5(strs).hexdigest()
        return md5

    def redisHset(self, key, item, name='tiankong'):
        """
        redis持久化
        """
        self.redis_res.hset(name, key, json.dumps(item, ensure_ascii=False))

    def start_requests(self):
        for url in self.start_urls:
            text = self.getRequest(url)
            yield text

    def parse(self):
        """
        获取类别规则
        """
        for html in self.start_requests():
            ehtml = etree.HTML(html)
            for url in ehtml.xpath('//li[@class="sub"]/a/@href')[1:3]:
                logger.info('链接：{}'.format(url))
                yield url

    def page_url(self):
        """
        获取页码规则
        """

        ids = self.page
        logger.info('页码：{}'.format(ids))
        for i in range(ids+1):
            url = self.page_urls.format(i)
            logger.info('列表页url：{}'.format(url))
            yield url

    def list_url(self):
        """
        获取列表页规则
        """
        for url in self.page_url():
            html = self.getRequest(url)
            ehtml = etree.HTML(html)
            for url in ehtml.xpath('//tbody/tr/td[2]/a/@href'):
                url = self.html_url.format(url)
                logger.info('详情页url：{}'.format(url))
                yield url

    def executeCmd(self, cmd):
        """
        命令行执行
        """
        try:
            logger.debug('cmd:{}'.format(cmd))
            os.system(cmd)
        except Exception as e:
            logger.error('error cmd异常：cmd:{}, 异常信息：{}'.format(cmd, e))

    def shop_html(self):

        """
        http://192.168.101.31:8181/docs/app-security/app-security-1ci4upcotsua0
        """
        for url in self.list_url():
            html = self.getRequest(url)
            ehtml = etree.HTML(html)
            item = defaultdict(str)
            item['downLoadUrl'] = ehtml.xpath('//*[@id="cp-url"]')
            item['shop'] = '天空下载'
            item['url'] = url
            item['spiderTime'] = time.strftime("%Y-%m-%d", time.localtime())
            logger.info('数据：{}'.format(item['name']))
            print(item)
            path_res = '{}/{}'.format(APK_DOEN, item['spiderTime'])
            self.executeCmd('maker {}'.format(path_res))
            # self.redisHset(apk_name, item)
            # apk_name = self.getMd5(item['downloadUrl'])
            # value = '{}|{}|{}/{}|{}|{}|{}'.format(item['downLoadUrl'], apk_name, APK_DOEN, apk_name, item['name'], item['shop'], item['url'])
            # self.redis_downurl.lpush(self.csvCont.get('url_key'), value)

if __name__ == '__main__':
    hj = BrowseSpider()
    hj.shop_html()