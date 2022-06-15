import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import RuleItem, RulespiderItem
import time

class HuyaSpider(CrawlSpider):
    name = 'jinli1'
    allowed_domains = ['game.gionee.com']
    start_urls = ['https://game.gionee.com/Front/Category/index/?action=visit&object=category']

    rules = (
        # 详情页url
        Rule(LinkExtractor(restrict_xpaths='//ul/li/a[@class="thumb"]'), callback='parse_item', follow=False, process_links='process_links'),
        # 翻页
        # Rule(LinkExtractor(restrict_xpaths='//div[@class="bd"]/div'), follow=True),
    )


    def process_links(self, lineks):
        for i, link in enumerate(lineks):
            # link.url = 'https://game.gionee.com/Front/Index/tj/?type=1&_url=https%3A%2F%2Fgame.gionee.com%2FFront%2FGame%2Fdetail%2F%3Fid%3D10248%26cku%3D113765630_null%26action%3Dvisit%26object%3Dgamedetail10248%26intersrc%3Dcategory100_new_gid10248'
            # print(i, link)
            yield link

    def parse_item(self, response):
        loader = RuleItem(item=RulespiderItem(), response=response)
        loader.add_xpath('name', '//div[@class="game_intro"]/h4/text()')
        loader.add_xpath('apksize', '.', re='大小：(.*?)<')
        loader.add_xpath('downloadUrl', '//p[@class="btn_area"]/a[2]/@href')
        loader.add_xpath('version', '.', re='版本：(.*?)<')
        loader.add_xpath('introduce', '//div[@id="j_content"]')
        loader.add_xpath('developer', '//li[@class="name"]/text()')
        loader.add_xpath('updatetime', '.', re='更新日期：(\d{4}-\d{2}-\d{2})<')
        loader.add_value('category', '游戏')
        loader.add_xpath('icon_url', '//div[@class="game_intro"]/a/img/@src')
        loader.add_xpath('sceenshot_url', '.', re='data-original="(.*?)"')
        loader.add_value('shop', '金立游戏商城')
        loader.add_value('system', 'android')
        loader.add_value('dlamount', 0)
        loader.add_value('url', response.url)
        loader.add_value('source', 'pc')
        loader.add_value('jsonObject', {'time': time.strftime("%Y-%m-%d", time.localtime())})
        yield loader.load_item()

