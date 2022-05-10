# Scrapy settings for eversec project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'eversec'

SPIDER_MODULES = ['eversec.spiders']
NEWSPIDER_MODULE = 'eversec.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'eversec (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 2
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'eversec.middlewares.EversecSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   'eversec.middlewares.RandomUserAgentMiddleware': 100,
   # 'eversec.middlewares.TestProxyMiddleware': 545,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'eversec.pipelines.EversecPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


DATABASE = {
     # 'kafka': {'product': ['192.168.205.163:9095'],
     #           'consumer': ['192.168.205.163:2181'],
     #        },
    'kafka': {'product': ['192.168.126.24:9092'],
              'consumer': ['192.168.126.24:2181'],
              },
    'redis_res': {
        'host': '172.17.0.2',
        'password': 'eversec123098',
        'db': 2,
        'port': 16379,
        'decode_responses': True
        },
    'redis_down': {
        'host': '172.17.0.2',
        'password': 'eversec123098',
        'db': 0,
        'port': 16379,
        'decode_responses': True
    },
    'REDIS_DOWN':'eversec_url_downloader.0703',
    'mysql': {},
    'files': {
        'weixin':'wechat.txt'
    },
    }
topic = 'app_info_topic'

csvFiles = '/home/crawler/csv/20220107_t_app_reptile.csv'

APK_DOEN = '/home/exe'

# log config
import datetime
Today = datetime.datetime.now()#取得现在的时间

import platform

if platform.system().lower() == 'windows':
    LOG_FILE = r'E:\gitlab\crawler-web\eversec\eversec\log\scrapy_{}_{}_{}.log'.format(Today.year, Today.month, Today.day)
else:
    LOG_FILE = '../log/scrapy_{}_{}_{}.log'.format(Today.year, Today.month, Today.day) #以时间为文件名

SCHEDULER = "scrapy_redis.scheduler.Scheduler"
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
SCHEDULER_PERSIST = False

REDIS_URL = 'redis://:eversec123098@127.0.0.1:6379'

# SCHEDULER_PERSIST = False


