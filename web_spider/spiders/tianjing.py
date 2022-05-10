from eversec.toKafka import KafkaTest
from eversec.settings import topic
import csv,json,redis
import time
import logging
import logging.handlers
logger = logging.getLogger('main')
logger.setLevel(level=logging.DEBUG)

# conn_pool = redis.ConnectionPool(**DATABASE['redis'])
# redis_con = redis.Redis(connection_pool=conn_pool)
#
# #handler = logging.FileHandler(logname, encoding='utf-8')
# handler = logging.handlers.RotatingFileHandler("log/{}".format(logname),  mode="a", maxBytes=5 * 1024 * 1024 * 1024, backupCount=10)
# handler.setLevel(logging.INFO)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)

def readCsv(files):
    filters = ['exe','zip']
    with open(files, encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            line_count += 1
            # if line_count == 1:
            #     continue
            # else:
            #     yield row
            if line_count <= 10:
                yield row

def getRes(res):
    item = dict()
    item['name'] = res[0]
    item['apksize'] = unit_conversion(res[2])
    item['system'] = 'android'
    item['downloadUrl'] = res[3]
    item['version'] = res[4]
    item['introduce'] = res[5]
    item['developer'] = res[6]
    item['category'] = res[7]
    item['icon_url'] = res[9]
    item['updatetime'] = res[8].replace('/', '-')
    item['sceenshot_url'] = [i.strip() for i in res[10].split(',')]
    item['shop'] = res[11]
    item['url'] = res[12]
    item['source'] = 'tj'
    item['province'] = res[13]
    item['city'] = res[14]
    item['dlamount'] = 0
    item['jsonObject'] = {'time': time.strftime("%Y-%m-%d", time.localtime())}
    return item

def getRes1(res):
    item = dict()
    item['name'] = res[0]
    item['apksize'] = unit_conversion(res[3])
    item['system'] = 'android'
    item['downloadUrl'] = res[4]
    item['version'] = res[5]
    item['introduce'] = res[6]
    item['developer'] = res[7].strip().replace('\\N', '')
    item['category'] = res[8]
    item['icon_url'] = res[12]
    item['updatetime'] = res[11].replace('/', '-')
    item['sceenshot_url'] = [i.strip() for i in res[13].split(',')]
    item['shop'] = res[14]
    item['url'] = res[15]
    item['source'] = 'tj'
    item['province'] = ''
    item['city'] = ''
    item['dlamount'] = 0
    item['jsonObject'] = {'time': time.strftime("%Y-%m-%d", time.localtime()),
                          'code': res[-1].strip().replace('\\N', '')
                          }
    return item

def unit_conversion(name):
    if 'M' in name:
        name = name.replace('M', '')
        return int(float(name) * 1024 * 1024)
    else:
        return int(name) if name else 0


def csvToRedis(key):
    for i in readCsv(csvFiles):
        msg = getRes(i)
        redis_con.lpush(key, json.dumps(msg, ensure_ascii=False))

def readRedis(numbers, key):
    for i in range(numbers):
        res = redis_con.blpop(key, 10)
        yield res

def main(files):
    kafka_ins = KafkaTest()
    for line in readCsv(files):
        item = getRes1(line)
        print(item)
        kafka_ins.async_produce_message(item, topic)

# if __name__ == '__main__':
    # main(r'E:\泰尔\徐州市app.csv')
    # main(r'E:\泰尔\20211001_20211015tj\20211001_20211015tj.csv')
    #csvToRedis(redis_key)
    # kafka_ins = KafkaTest()
    # logger.info('set_num:{}'.format(set_num))
    # main(set_num, redis_key)
