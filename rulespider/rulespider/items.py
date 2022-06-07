# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field

class RulespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
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
