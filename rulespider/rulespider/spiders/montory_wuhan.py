import scrapy
from scrapy.http import JsonRequest
import logging
from scrapy.utils.project import get_project_settings
from datetime import date, timedelta
import os
logger = logging.getLogger(__name__)

class PopwuhanSpider(scrapy.Spider):
    name = 'monitory'
    # allowed_domains = ['58.49.62.62:58090']
    # start_urls = ['http://58.49.62.62:58090/db/monitorAppData']
    start_urls = ['https://www.baidu.com/']
    settings = get_project_settings()
    yesterday = (date.today() + timedelta(days=-1)).strftime("%Y-%m-%d")

    def execute_cmd(self, cmd):
        return os.popen(cmd).read()

    def get_data(self):
        item = {}
        item['projectName'] = '武汉'
        item['monitorDate'] = self.yesterday
        item['isSys'] = 0
        req_file = self.settings['LOG_FILE']
        down_file = '/home/crawl_downloader/LOG/crawl_downloader_manager.log'
        # 请求量
        cmd1 = 'grep {} {} | wc -l'.format(self.settings['topic'], req_file)
        item['appCrawlerNum'] = int(self.execute_cmd(cmd1))
        # 下载量
        cmd2 = 'grep "发送消息" {} |grep {} | wc -l'.format(self.yesterday, down_file)
        item['appDownloadNum'] = int(self.execute_cmd(cmd2))
        # 下载成功量
        cmd3 = 'grep "发送消息" {} | grep {} | grep SUCCESS| wc -l'.format(self.yesterday, down_file)
        item['appDownloadSuccessNum'] = int(self.execute_cmd(cmd3))
        # 下载失败量
        item['appDownloadErrorNum'] = item['appDownloadNum'] - item['appDownloadSuccessNum']
        return item

    def start_requests(self):
        data = self.get_data()
        print(data)
        # for url in self.start_urls:
        #     data = {"_id": "48706284397", "date": "2022-06-27", "appName": "华为应用市场", "appCrawlerNum": "45", "isSys": "0", "projectName": "武汉"}
        #     yield JsonRequest(url=url, data=data, callback=self.parse)

    def parse(self, response):
        print(response.json())
        print(self.settings['LOG_FILE'])