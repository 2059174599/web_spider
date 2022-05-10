import os
import requests
import re
import time
import datetime
import xlwt
import logging
# from eversec.settings import Log_file_path


logger = logging.getLogger('SpiderExcel')
# logger.setLevel(level=logging.INFO)
# handler = logging.handlers.RotatingFileHandler(Log_file_path,  mode="a", encoding='utf-8')
# handler.setLevel(logging.INFO)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)

class SpiderExcel(object):
    """
    定时生成excel
    """

    def __init__(self, beg, end, page=1):
        self.page = page
        # 创建工作簿
        self.workbook = xlwt.Workbook(encoding='utf-8')
        # 创建sheet
        self.data_sheet = self.workbook.add_sheet('Sheet1')
        self.default = self.set_style('Times New Roman', 220, True)
        self.beg = beg
        self.end = end
        self.url = 'http://10.96.217.64/miner/list?beginDate={}&endDate={}&page={}&ip=&symbolId=&entity=&subRegion=&limit=100'
        self.headers = {
            'Host': '10.96.217.64',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8',
           'Cookie': 'advanced-backend=522b3a93ae168403218e2c2c992e0cf4; _csrf-backend=953db2b43263fff187268a86a0b37767b82c6df524e115d48dd083dfeff6603fa%3A2%3A%7Bi%3A0%3Bs%3A13%3A%22_csrf-backend%22%3Bi%3A1%3Bs%3A32%3A%22dGR7ZJ13HLcZgLXx-sqj26dK0iVEe7I7%22%3B%7D; _identity-backend=99fab01c5368c75fbae7b88bab4e41ae48457f3510963fc9a87dccb9c7a5b95da%3A2%3A%7Bi%3A0%3Bs%3A17%3A%22_identity-backend%22%3Bi%3A1%3Bs%3A47%3A%22%5B82%2C%22I-c8f0VvTYI1wugguEMmZXVwbouDduVr%22%2C2592000%5D%22%3B%7D',
          }

    def set_style(self,name, height, bold=False):
        style = xlwt.XFStyle()  # 初始化样式
        font = xlwt.Font()  # 为样式创建字体
        font.name = name
        font.bold = bold
        # font.color_index = 4
        font.height = height
        style.font = font
        return style

    def getHtml(self, url):
        r = requests.get(url, headers=self.headers).text
        return r

    def readText(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            res = f.read()
        return res

    def cmd(self, cmds):
        os.system(cmds)

    def writeText(self, path, res):
        with open(path, 'a', encoding='utf-8') as f:
            f.write(res)

    def getPage(self):
        url = self.url.format(self.beg, self.end, self.page)
        logger.info('获取页码url：{}'.format(url))
        # html = self.getHtml(url)
        html = self.readText('html.txt')
        numb = re.search('记录数：(.*?)</div>', html, re.S).group(1)
        remainder = int(numb) % 100
        page = int(numb) // 100 if remainder == 0 else int(numb) // 100 + 1
        logger.info('页码：{}'.format(page))
        return 1

    def getRes(self, html):
        res_list = re.findall('<td><a href=.*?>(.*?)</a></td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>', html, re.S)
        return res_list

    def write_excel(self, path, rows):
        """
        写入Excel
        """
        j = k = 0
        # 循环读取每一行数据并写入Excel
        for row in rows:
            for i in range(len(row)):
                try:
                    # 写入
                    self.data_sheet.write((j + k), i, row[i], self.default)
                except Exception as e:
                    logging.error('写入excel异常：{}'.format(e))
                    logging.error('异常数据：{}'.format(row))
                    continue
                # data_sheet.write(1, i, row1[i], self.set_style('Times New Roman', 220, True))
            k = k + 1
        self.workbook.save(path)
        logger.info('写入文件成功，共{}行数据'.format(k))
        print("写入文件成功，共" + str(k) + "行数据")

    def main(self, path):
        rows = [('矿工IP', '矿工端口','首次发现时间', '矿池IP', '设备总数', '矿池端口', '币种', '特定矿池矿工数', 'ETH 算力（MH/s）', 'BTC 算力（GH/s）','提交次数', '单位', '省份', '城市')]
        page = self.getPage()
        if page == 1:
            url = self.url.format(self.beg, self.end, self.page)
            # html = self.getHtml(url)
            html = self.readText('html.txt')
            res = self.getRes(html)
            if res:
                rows += res
            else:
                logger.info('空数据url:{}'.format(url))
        elif page > 1:
            for i in range(1, page+1):
                url = self.url.format(self.beg, self.end, i)
                html = self.getHtml(url)
                res = self.getRes(html)
                if res:
                    rows += res
                else:
                    logger.info('空数据url:{}'.format(url))
        self.write_excel(path, rows)


if __name__ == '__main__':
    now_time = datetime.datetime.now()
    beg = (now_time + datetime.timedelta(days=-2)).strftime("%Y-%m-%d")
    end = (now_time + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
    fj = SpiderExcel(beg, end)
    path = '{}_{}.xlsx'.format(beg, end)
    fj.main(path)





