# from scrapy import cmdline
# cmdline.execute('scrapy crawl xiaomi'.split())
import argparse

from scrapy.utils.project import get_project_settings
from rulespider.utils import get_config
from scrapy.crawler import CrawlerProcess

parser = argparse.ArgumentParser(description='universal spider')
parser.add_argument('name', help='name of spider tu run')
args = parser.parse_args()
name = args.name

def run():
    config = get_config(name)
    spider = config.get('spider', 'universal')
    project_settings = get_project_settings()
    settings = dict(project_settings.copy())
    settings.update(config.get('settings'))
    process = CrawlerProcess(settings)
    process.crawl(spider, **{'name':name})
    process.start()

if __name__ == '__name__':
    run()