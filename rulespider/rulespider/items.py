# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, Identity, Compose

class RulespiderItem(scrapy.Item):
    # define the fields for your item here like:
    _id = Field()
    name = Field()
    apksize = Field()
    downloadUrl = Field()
    version = Field()
    introduce = Field()
    developer = Field()
    category = Field()
    updatetime = Field()
    icon_url = Field()
    sceenshot_url = Field()
    dlamount = Field()
    shop = Field()
    url = Field()
    jsonObject = Field()
    system = Field()
    province = Field()
    city = Field()
    source = Field()

class RuleItem(ItemLoader):
    default_output_processor = TakeFirst()
    # 取列表
    sceenshot_url_out = Identity()
    # 去空格
    name_out = Compose(TakeFirst(), str.strip)
