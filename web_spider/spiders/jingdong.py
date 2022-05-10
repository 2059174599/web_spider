import random

import requests, re, json
from lxml import etree
import time
from fake_useragent import UserAgent
ue = UserAgent()


def get_proxies():
    """
    拿代理
    :return:
    """
    r = requests.get('http://api.ip.data5u.com/dynamic/get.html?order=39a2d4b24d9c2f068095ef80f95662ae').text.strip()
    if r:
        return {'http': 'http://{}'.format(r)}
    else:
        print('error: 代理异常 {}'.format(r))

def getHtml(url):
    headers = {
        'user-agent': ue.random,
        'cookie': '__jdu=354999398; areaId=1; PCSYCityID=CN_110000_110100_0; shshshfpa=84fedd19-b66a-7701-1df5-a51004cdabfe-1644474326; unpl=JF8EAK1nNSttUElTB0tSGUESSFRXWwlbGB8CazQMBF0LGQAAHFIaFkR7XlVdXhRKFB9vZhRUWVNLVg4ZACsSEXteXVdZDEsWC2tXVgQFDQ8VXURJQlZAFDNVCV9dSRZRZjJWBFtdT1xWSAYYRRMfDlAKDlhCR1FpMjVkXlh7VAQrAB8XGENVVlZUOHsQM19XA1NaX0JdNRoyGiJSHwFTV1UBSRRObWMAXFVQSVwMKwMrEQ; __jdv=76161171|baidu-pinzhuan|t_288551095_baidupinzhuan|cpc|0f3d30c8dba7459bb52f2eb5eba8ac7d_0_9363aa3b32824ebb905b8a1bce46a05e|1644477214401; shshshfpb=dKSjgEkK_2Emx0fOVeqwUTQ; __jdc=122270672; shshshfp=edd46f589104e7bc0c2c445a0554212d; ipLoc-djd=1-2802-54745-0; mt_xid=V2_52007VwEWV1VQWlgXQCleAjQDQlBZCk4IG01JQABgVEdODgxQDQNBGVoFZlcRVAhcAV0vShhfBnsCEU5dWENaGkIcWg5nAiJQbVhiXhhJEFwAZgsXW21YVF4b; ip_cityCode=2802; __jda=122270672.354999398.1644474322.1644565871.1644568991.7; wlfstk_smdl=e9kvqy7w8yx6jkpxpdyf95wgd0vhkw5y; thor=9BD69C043DA9CF1E9154AC5E5012EC9F46648954109FF7A3293A17A53361B5D9E90A237719A3AAB95D7FF8A05D1E714F00E232C2D15CC14023EC6AA139E63CFF5B1E75B2A01015929E77D68E9E6A8C6DD26368D1C1DB63DF087597376A346EDCFE76B049ED6E2B1A7C9F443BC131208334A726AA23C9CFF516C6E2999F96C1042CB73E9D7E8F7D28D358C28B7CB51F51; pinId=3JMo5ZnfKxhis4dZqOHMJQ; pin=18338767283_p; unick=Mr-%E5%BE%B7%E5%85%88%E7%94%9F; ceshi3.com=201; _tp=v0n48%2BopaKeB%2Ftus4yyLSQ%3D%3D; _pst=18338767283_p; token=48d253f32cd3e536436b785e38d81e53,3,913650; __tk=ec6360b9767a1c544abc13cafa339286,3,913650; shshshsID=2eead7b8ffe50d878d51cbd4044efd51_3_1644571749063; __jdb=122270672.9.354999398|7.1644568991; 3AB9D23F7A4B3C9B=4NBSUKLLA4QNFVVMHT2PLZL3ZBNAFS7VF2BTCPXEUSMKWCFRMFPLGCFSUQCNY6O73OSHDPW7NBK26ZOSAKWJASAR2U'
    }
    r = requests.get(url ,headers=headers).text
    return r

def getListUrl(html):
    # print(html)
    html = etree.HTML(html)
    urls = html.xpath('//*[@id="J_goodsList"]/ul/li/div/div[1]/a/@href')
    prices = html.xpath('//*[@id="J_goodsList"]/ul/li/div/div[2]/strong/i/text()')
    urls_list = []
    for i in urls:
        if 'http' in i:
            urls_list.append(i)
        else:
            urls_list.append('https:'+i)
    return urls_list, prices

def getRe(strs, html):
    try:
        return re.search(strs, html).group(1)
    except:
        return ''

def getItem(html, url, price):
    item = {}
    item['net_conent'] = getRe(r'净含量</dt><dd>(.*?)</dd>', html)
    item['expiration_date'] = getRe(r'保质期</dt><dd>(.*?)</dd>', html)
    item['production_licence'] = getRe(r'生产许可证号</dt><dd>(.*?)</dd>', html)
    item['product_standard_code'] = getRe(r'产品标准号</dt><dd>(.*?)</dd>', html)
    item['url'] = url
    item['price'] = price
    # comts = getCommit(url)
    # if comts:
    #     item['commit'] = {'comment': comts[0], 'comment_bad': comts[1]}
    return item

def getCommit(url):
    ids = getRe(r'([0-9]+)', url)
    print(ids)
    if len(ids) > 3:
        comment_url = 'https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98&productId={}&score=0&sortType=5&page=1&pageSize=10&isShadowSku=0&rid=0&fold=1'.format(ids)
        comments_url = 'https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98&productId={}&score=1&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1'.format(ids)
        comment = []
        comments = []
        html = getHtml(comment_url)
        htmls = getHtml(comments_url)
        # print(htmls)
        html = getRe(r'fetchJSON_comment98\((.*?)\);', html)
        htmls = getRe(r'fetchJSON_comment98\((.*?)\);', htmls)
        # print(htmls)
        for i in json.loads(html)['comments']:
            item = {}
            item['name'] = i['nickname']
            item['content'] = i['content']
            item['creationTime'] = i['creationTime']
            comment.append(item)
        for j in json.loads(htmls)['comments']:
            items = {}
            items['name'] = j['nickname']
            items['content'] = j['content']
            items['creationTime'] = j['creationTime']
            comments.append(items)
        return comment, comments

def saveResult(item):
    with open(r'E:\泰尔\result.text', 'a', encoding='utf-8') as f:
        f.write(item+'\n')

def main():
    for j in range(9, 50):
        url = 'https://list.jd.com/list.html?cat=1320%2C1583%2C1590&page={}&s=177&click=0'.format(j)
        html = getHtml(url)
        urls, prices = getListUrl(html)
        print(urls, prices)
        for i in range(len(urls)):
            try:
                time.sleep(random.randint(5, 15))
                html = getHtml(urls[i])
                # print('%%%%%%', html)
                item = getItem(html, urls[i], prices[i])
                print('****', item)
                saveResult(json.dumps(item, ensure_ascii=False))
            except Exception as e:
                print('error', e)
                time.sleep(random.randint(3,20))
                continue

# main()
# print(get_proxies())