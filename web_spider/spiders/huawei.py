from eversec.toKafka import KafkaTest
import csv,json,redis,requests
import time,os
import logging
import logging.handlers
logger = logging.getLogger('main')
logger.setLevel(level=logging.DEBUG)
topic = 'app_info_topic'

def readCsv(files):
    filters = ['exe','zip']
    with open(files,'r', encoding='utf-8') as csv_file:
        line_count = 0
        for row in csv_file:
            line_count += 1
            # if line_count == 1:
            #     continue
            # else:
            #     yield row
            if line_count <= 10000000000:
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
    item['name'] = res[1]
    item['apksize'] = res[5]
    item['system'] = 'android'
    item['downloadUrl'] = res[8]
    item['version'] = res[4]
    item['introduce'] = ''
    item['developer'] = res[9]
    item['category'] = res[7]
    item['icon_url'] = res[2]
    item['updatetime'] = res[10].split(' ')[0]
    item['sceenshot_url'] = ''
    item['shop'] = '华为应用市场'
    item['url'] = 'https://appstore.huawei.com/app/{}'.format(res[0])
    item['source'] = 'phone'
    url = 'https://app.eversaas.cn/service/app-ops/gaodeinfo?str={}'.format(item['developer'])
    data = requests.get(url).text
    data = json.loads(data)
    if data['body']:
        item['province'] = data['body']['province'] if data['body']['province'] else ''
        item['city'] = data['body']['city'] if data['body']['city'] else ''
    else:
        item['province'] = ''
        item['city'] = ''
    item['dlamount'] = unit_conversion(res[6].replace(',',''))
    item['jsonObject'] = {'time': time.strftime("%Y-%m-%d", time.localtime()),
                          'privacy_url': res[-1].strip()
                          }
    return item

def unit_conversion(name):
    try:
        if '十万次安装' in name:
            name = name.replace('十万次安装', '').strip()
            return int(float(name) * 100000)
        if '百万次安装' in name:
            name = name.replace('百万次安装', '').strip()
            return int(float(name) * 1000000)
        if '千万次安装' in name:
            name = name.replace('千万次安装', '').strip()
            return int(float(name) * 10000000)
        if '万次安装' in name:
            name = name.replace('万次安装', '').strip()
            return int(float(name) * 10000)
        if '亿次安装' in name:
            name = name.replace('亿次安装', '').strip()
            return int(float(name) * 100000000)
        if '十亿次安装' in name:
            name = name.replace('十亿次安装', '').strip()
            return int(float(name) * 1000000000)
    except:
        return 0


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
        item = getRes1(line.split('\t'))
        print(item)
        kafka_ins.async_produce_message(item, topic)

def file_name(file_dir):
    for root, dirs, files in os.walk(file_dir):
        print(root) #当前目录路径
        print(dirs) #当前路径下所有子目录
        for file in files:
            yield '{}\{}'.format(root,file)

if __name__ == '__main__':
    for file in file_name('/home/eversec/spiders/data/huawei'):
        main(file)
