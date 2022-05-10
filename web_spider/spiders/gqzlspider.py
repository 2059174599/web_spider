import scrapy


class GqzlspiderSpider(scrapy.Spider):
    name = 'gqzlspider'
    headers = {
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
    keys = ['vehicles']
    pages = 1

    def start_requests(self):
        for key in self.keys:
            for page in range(self.pages):
                data = 'number=%E8%AF%B7%E8%BE%93%E5%85%A5%E7%B2%BE%E7%A1%AE%E7%BC%96%E5%8F%B7&startDate=&endDate=&flag=%5BLjava.lang.String%3B%406e253464&field=&order=&keyword={}&condition=1&keywordFlag=0&cnvdId=&cnvdIdFlag=0&baseinfoBeanbeginTime=&baseinfoBeanendTime=&baseinfoBeanFlag=0&refenceInfo=&referenceScope=-1&manufacturerId=-1&categoryId=-1&editionId=-1&causeIdStr=&threadIdStr=&serverityIdStr=&positionIdStr=&numPerPage=10&offset={}&max=10'.format(key,page*10)
                data = 'number=%E8%AF%B7%E8%BE%93%E5%85%A5%E7%B2%BE%E7%A1%AE%E7%BC%96%E5%8F%B7&startDate=&endDate=&flag=%5BLjava.lang.String%3B%406e253464&field=&order=&keyword={}&condition=1&keywordFlag=0&cnvdId=&cnvdIdFlag=0&baseinfoBeanbeginTime=&baseinfoBeanendTime=&baseinfoBeanFlag=0&refenceInfo=&referenceScope=-1&manufacturerId=-1&categoryId=-1&editionId=-1&causeIdStr=&threadIdStr=&serverityIdStr=&positionIdStr=&numPerPage=10&offset={}&max=10'.format(key,page*10)
                url = 'https://www.cnvd.org.cn/flaw/list.htm?flag=true'
                yield scrapy.Request(url=url, method='post', headers=self.headers, body=data, callback=self.parse)
                # scrapy.Request
                # import requests
                # requests.post()


    def parse(self, response):
        print('*************')
        print(response.text)

