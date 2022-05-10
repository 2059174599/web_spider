import requests, json, time, hashlib, datetime
import logging

import logging.handlers

logger = logging.getLogger('covid')
logger.setLevel(level=logging.INFO)
handler = logging.handlers.RotatingFileHandler('covid.log',  mode="a", encoding='utf-8')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class NewsSpider(object):
    """
    疫情信息采集
    1.  风险地区、风险等级
    https://news.qq.com/zt2020/page/feiyan.htm#/

    疫情咨询播报
    https://i.snssdk.com/ugc/hotboard_fe/hot_list/template/hot_list/forum_tab.html?activeWidget=1&show_share=0

    疫情病例统计
    https://news.qq.com/zt2020/page/feiyan.htm#/

    """
    def __init__(self):
        pass

    def riskArea(self, times):
        result = []
        e = int(time.time())
        string1 = '{}'.format(e) + '23y0ufFl5YxIyGrI8hWRUZmKkvtSjLQA' + '123456789abcdefg' + '{}'.format(e)
        signatureHeader = hashlib.sha256(string1.encode("utf-8")).hexdigest().upper()
        string2 = '{}'.format(e) + 'fTN2pfuisxTavbTuYVSsNJHetwq5bJvCQkjjtiLM2dCratiA' + '{}'.format(e)
        signature = hashlib.sha256(string2.encode("utf-8")).hexdigest().upper()
        heads = {'Accept': 'application/json, text/javascript, */*; q=0.01',
                 'Accept-Encoding': 'gzip, deflate, br',
                 'Accept-Language': 'zh-CN,zh;q=0.9',
                 'Cache-Control': 'no-cache',
                 'Connection': 'keep-alive',
                 'Content-Type': 'application/json; charset=UTF-8',
                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
                 'x-wif-nonce': 'QkjjtiLM2dCratiA',
                 'x-wif-paasid': 'smt-application',
                 'x-wif-signature': signature,
                 'x-wif-timestamp': '{}'.format(e)}

        data = {
            'appId': "NcApplication",
            'key': "3C502C97ABDA40D0A60FBEE50FAAD1DA",
            'nonceHeader': "123456789abcdefg",
            'paasHeader': "zdww",
            'signatureHeader': signatureHeader,
            'timestampHeader': '{}'.format(e),
        }
        url = 'https://bmfw.www.gov.cn/bjww/interface/interfaceJson'
        r = requests.post(url, headers=heads, json=data).text
        data = json.loads(r)['data']
        # print(data)
        highlist = data['highlist']
        middlelist = data['middlelist']
        for line in highlist:
            province = line['province']
            city = line['city']
            county = line['county']
            for community in line['communitys']:
                res = '{}&&&{}{}{}{}&&&{}'.format(1, province, city, county, community, times)
                result.append(res)

        for line in middlelist:
            province = line['province']
            city = line['city']
            county = line['county']
            for community in line['communitys']:
                res = '{}&&&{}{}{}{}&&&{}'.format(2, province, city, county, community, times)
                result.append(res)
        return result

    def covidCase(self):
        result = []
        heads = {'Accept': '*/*',
                 'Accept-Encoding': 'gzip, deflate, br',
                 'Accept-Language': 'zh-CN,zh;q=0.9',
                 'Cache-Control': 'no-cache',
                 'Connection': 'keep-alive',
                 # 'Content-Length': '0',
                 # 'Content-Type': 'application/x-www-form-urlencoded',
                 # 'Host': 'api.inews.qq.com',
                 # 'Origin': 'https://news.qq.com',
                 # 'Pragma': 'no-cache',
                 # 'Referer': 'https://news.qq.com/',
                 # 'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
                 # 'sec-ch-ua-mobile': '?0',
                 # 'sec-ch-ua-platform': '"Windows"',
                 # 'Sec-Fetch-Dest': 'empty',
                 # 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-site',
                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'}
        url = 'https://api.inews.qq.com/newsqa/v1/query/inner/publish/modules/list?modules=statisGradeCityDetail,diseaseh5Shelf'
        r = requests.post(url, headers=heads).text
        data = json.loads(r)['data']
        times = data['diseaseh5Shelf']['lastUpdateTime']
        for line in data['statisGradeCityDetail']:
            province = line['province']
            city = line['city']
            added = line['confirmAdd']
            existed = line['nowConfirm']
            res = '1&&&{}&&&{}&&&{}&&&{}&&&{}'.format(province, city, added, existed, times)
            result.append(res)
        return result, times

    def getNews(self):
        result = []
        heads = {'Accept': '*/*',
                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'}
        url = 'https://i.snssdk.com/api/amos_items/7010702099348619277/1711799492831309/?activeWidget=1&show_share=0&category=forum_flow_subject&stream_api_version=82&aid=13&offset=0&count=60'

        r = requests.post(url, headers=heads).text
        data = json.loads(r)['item_cells']
        for line in data:
            #     print(line)
            raw_data = json.loads(line['raw_data'])
            #     print(raw_data['timestamp'])
            timeArray = time.localtime(raw_data['timestamp'])  # 转化成对应的时间
            otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)  # 字符串
            yesterday = (datetime.date.today() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
            if yesterday in otherStyleTime:
                res = '1&&&{}&&&{}&&&{}'.format(raw_data['title'], raw_data['text'], otherStyleTime)
                result.append(res)
        return result

    def main(self):
        try:
            item = dict()
            logger.info('开始采集 covidRes')
            covidRes, times = self.covidCase()
            logger.info('开始采集 riskRes')
            item['covidRes'] = covidRes
            riskRes = self.riskArea(times)
            item['riskRes'] = riskRes
            newsRes = self.getNews()
            item['newsRes'] = newsRes
            return {'status':200, 'data':item}
        except Exception as e:
            logger.error('e')
            return None


if __name__ == '__main__':
    newsspider= NewsSpider()
    res = newsspider.main()
    print(res)
