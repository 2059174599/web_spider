# Scrapy settings for rulespider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'rulespider'

SPIDER_MODULES = ['rulespider.spiders']
NEWSPIDER_MODULE = 'rulespider.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'rulespider (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 1
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

DOWNLOAD_FAIL_ON_DATALOSS = False
# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'rulespider.middlewares.RulespiderSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   'rulespider.middlewares.RulespiderDownloaderMiddleware': 100,
    # 'rulespider.middlewares.RandomUserAgentMiddleware': 100,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'rulespider.pipelines.RulespiderPipeline': 300,
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

import datetime
Today = datetime.datetime.now() #取得现在的时间
LOG_FILE = '../log/scrapy_{}_{}_{}.log'.format(Today.year, Today.month, Today.day)

SCHEDULER = "scrapy_redis.scheduler.Scheduler"
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# 布隆过滤器
# DUPEFILTER_CLASS = "scrapy_redis_bloomfilter.dupefilter.RFPDupeFilter"
# BLOOMFILTER_HASH_NUMBER = 6
# 128MB 1亿数量级
# BLOOMFILTER_BIT = 30
SCHEDULER_PERSIST = False
FIT_NAMES = ['apksize', 'developer', 'downloadUrl']
REDIS_URL = 'redis://:eversec123098@10.0.4.38:6379'
# 分区名称
REDIS_KEY = 'wuhan'
MONGO_URL = 'mongodb://root:eversec123098@127.0.0.1:27001'
MONGO_DATABASES = 'test'
MONGO_COLLECTION = 'app_info'
POST_URL = 'http://10.0.4.38:8090/db/pushAppData'
POP_URL = 'http://58.49.62.62:58090/db/popAppData?name={}'.format(REDIS_KEY)
PROXY_API = 'http://13810804359.user.xiecaiyun.com/api/proxies?action=getText&key=NPEB017FC8&count=1&word=&rand=false&norepeat=false&detail=false&ltime=0'
KAFKA = {'product': ['10.0.4.33:9092'],
         'consumer': ['10.0.4.33:2181'],
          }
TOPIC = 'web_crawler_app_info_topic1'