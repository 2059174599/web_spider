import scrapy,json


class GqzlspiderSpider(scrapy.Spider):
    name = 'cnnvd'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'zh-CN,zh;q=0.9', 'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive', 'Content-Length': '434', 'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': '__jsluid_s=fc4c2698619f6f9a48e5b4f6ca20648f; JSESSIONID=20402376908FFF9EEF79BB16991448DC',
        'Host': 'www.cnvd.org.cn', 'Origin': 'https://www.cnvd.org.cn',
        'Referer': 'https://www.cnvd.org.cn/flaw/list.htm?flag=true',
        'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"', 'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin', 'Sec-Fetch-User': '?1', 'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'}
    keys = ['linux']
    pages = 2

    def start_requests(self):
        print('进入 spider**********')
        for key in self.keys:
            print('key',key)
            for page in range(1,self.pages):
                print('page',page)
                data = 'CSRFToken=&cvHazardRating=&cvVultype=&qstartdateXq=&cvUsedStyle=&cvCnnvdUpdatedateXq=&cpvendor=&relLdKey=&hotLd=&isArea=&qcvCname={}&qcvCnnvdid=CNNVD%E6%88%96CVE%E7%BC%96%E5%8F%B7&qstartdate=&qenddate='.format(key)
                data = {'CSRFToken': '',
                         'cvHazardRating': '',
                         'cvVultype': '',
                         'qstartdateXq': '',
                         'cvUsedStyle': '',
                         'cvCnnvdUpdatedateXq': '',
                         'cpvendor': '',
                         'relLdKey': '',
                         'hotLd': '',
                         'isArea': '',
                         'qcvCname': 'linux',
                         'qcvCnnvdid': 'CNNVD%E6%88%96CVE%E7%BC%96%E5%8F%B7',
                         'qstartdate': '',
                         'qenddate': ''}
                url = 'http://www.cnnvd.org.cn/web/vulnerability/queryLds.tag?pageno={}&repairLd='.format(page)
                print('999999999999')
                yield scrapy.FormRequest(url=url, method='post', headers=self.headers, formdata=data, callback=self.parse)
                # scrapy.Request
                # import requests
                # requests.post()


    def parse(self, response):
        print('*************')
        print(response.text)

