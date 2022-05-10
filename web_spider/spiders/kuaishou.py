import requests
import json
import re
from collections import defaultdict
import time


class Kuaishou(object):
    def __init__(self, refer=None):
        self.url = 'https://www.kuaishou.com/graphql'
        self.videoUrl = 'https://www.kuaishou.com/short-video'
        self.authorUrl = 'https://www.kuaishou.com/profile'
        self.headers = {'Accept-Encoding': 'gzip, deflate, br',
                         'Accept-Language': 'zh-CN,zh;q=0.9',
                         'Connection': 'keep-alive',
                         'Content-Length': '552',
                         'content-type': 'application/json',
                         'Cookie': 'clientid=3; did=web_a256a10d36b3d4ed569e291bca31d610; client_key=65890b29; didv=1623837694141; kpf=PC_WEB; kpn=KUAISHOU_VISION; _bl_uid=L1k2vr8Iakk2aLu312a69La7v0C9; userId=2382786919; kuaishou.server.web_st=ChZrdWFpc2hvdS5zZXJ2ZXIud2ViLnN0EqABnYxzTiqpH3qakDNbntQHbEYaeC-pKcaEhVmm66lSuGI4LHbs4IpkG34FzT_Sx73p0tx1Qg8M_RlIATRZ5ssyQCCL30XtObncQeaq-un1BIKw58CAknpBcl3ChVD36gEd8aAwPWjfyNLgjUIiBGfXHIWr_Esal2Wzf1wzRWfIppzKKcUI1Dr4WUf6AuRTAtzl7c4xm3ukxuDAMEe3lmEtSRoSnIqSq99L0mk4jolsseGdcwiNIiATb7-VYl5ZpO-DtVsG3a6OUOLxQ1lh4eAyaPF3tI3dASgFMAE; kuaishou.server.web_ph=fe8bff7641421166b5c301f3699379e40beb',
                         'Host': 'www.kuaishou.com',
                         'Origin': 'https://www.kuaishou.com',
                         # 'Referer': 'https://www.kuaishou.com/profile/3x2fq6my5mmrvak',
                         'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"', 'sec-ch-ua-mobile': '?0',
                         'Sec-Fetch-Dest': 'empty',
                         'Sec-Fetch-Mode': 'cors',
                         'Sec-Fetch-Site': 'same-origin',
                         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                         }

    def getHotKey(self):
        """
        热词
        热度
        """
        res = []
        headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                   'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'zh-CN,zh;q=0.9', 'Host': 'www.kuaishou.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                   }
        html = requests.get('https://www.kuaishou.com/',headers=headers).text
        hotKey = re.findall('id":"VisionHotRankItem:(.*?)",', html)
        for i in hotKey:
            item = dict()
            item['hotValue'] = re.search('name":"{}","viewCount":null,"hotValue":"(.*?)"'.format(i),html).group(1)
            item['key'] = i
            res.append(item)
        return res
    def homePage(self, ids):
        """
        粉丝数据
        """
        data = {"operationName":"visionProfile",
                "variables":{"userId":ids},
                "query":"query visionProfile($userId: String) {\n  visionProfile(userId: $userId) {\n    result\n    hostName\n    userProfile {\n      ownerCount {\n        fan\n        photo\n        follow\n        photo_public\n        __typename\n      }\n      profile {\n        gender\n        user_name\n        user_id\n        headurl\n        user_text\n        user_profile_bg_url\n        __typename\n      }\n      isFollowing\n      __typename\n    }\n    __typename\n  }\n}\n"
                }
        data = requests.post(url=self.url, headers=self.headers, json=data).text
        return json.loads(data)['data']['visionProfile']['userProfile']['ownerCount']

    def hotRoot(self, hotKey):
        """
        热词对应的链接
        """
        data = {"operationName": "hotVideoQuery", "variables": {"trendingId": hotKey, "page": "detail"},
                 "query": "query hotVideoQuery($trendingId: String, $page: String, $webPageArea: String) {\n  hotData(trendingId: $trendingId, page: $page, webPageArea: $webPageArea) {\n    result\n    llsid\n    expTag\n    serverExpTag\n    pcursor\n    webPageArea\n    feeds {\n      type\n      trendingId\n      author {\n        id\n        name\n        headerUrl\n        following\n        headerUrls {\n          url\n          __typename\n        }\n        __typename\n      }\n      photo {\n        id\n        duration\n        caption\n        likeCount\n        realLikeCount\n        coverUrl\n        photoUrl\n        coverUrls {\n          url\n          __typename\n        }\n        timestamp\n        expTag\n        animatedCoverUrl\n        stereoType\n        videoRatio\n        __typename\n      }\n      canAddComment\n      llsid\n      status\n      currentPcursor\n      __typename\n    }\n    __typename\n  }\n}\n"
                 }
        return requests.post(url=self.url,headers=self.headers,json=data).text

    def getPhotoIds(self,hotKey):
        """
        拿点赞
        """
        res = []
        item = json.loads(self.hotRoot(hotKey))['data']['hotData']['feeds']
        for i in item:
            line = dict()
            line['diggCount'] = i['photo']['likeCount']
            line['realLikeCount'] = i['photo']['realLikeCount']
            line['photoId'] = i['photo']['id']
            line['authorId'] = i['author']['id']
            line['hotKey'] = hotKey
            line['commentCount'] = self.getComment(line['photoId'])
            res.append(line)
        return res

    def getComment(self, photoId):
        """
        拿评论数据
        """
        jsons = {"operationName":"commentListQuery","variables": {"photoId": photoId,"pcursor":""},
                "query":"query commentListQuery($photoId: String, $pcursor: String) {\n  visionCommentList(photoId: $photoId, pcursor: $pcursor) {\n    commentCount\n    pcursor\n    rootComments {\n      commentId\n      authorId\n      authorName\n      content\n      headurl\n      timestamp\n      likedCount\n      realLikedCount\n      liked\n      status\n      subCommentCount\n      subCommentsPcursor\n      subComments {\n        commentId\n        authorId\n        authorName\n        content\n        headurl\n        timestamp\n        likedCount\n        realLikedCount\n        liked\n        status\n        replyToUserName\n        replyTo\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"
                }
        data = requests.post(url=self.url, headers=self.headers, json=jsons).text
        return json.loads(data)['data']['visionCommentList']['commentCount']

    def getFeeds(self):
        data = {"operationName":"brilliantTypeDataQuery","variables":{"hotChannelId":"00","page":"brilliant","pcursor":"1"},"query":"fragment feedContent on Feed {\n  type\n  author {\n    id\n    name\n    headerUrl\n    following\n    headerUrls {\n      url\n      __typename\n    }\n    __typename\n  }\n  photo {\n    id\n    duration\n    caption\n    likeCount\n    realLikeCount\n    coverUrl\n    photoUrl\n    coverUrls {\n      url\n      __typename\n    }\n    timestamp\n    expTag\n    animatedCoverUrl\n    distance\n    videoRatio\n    liked\n    stereoType\n    __typename\n  }\n  canAddComment\n  llsid\n  status\n  currentPcursor\n  __typename\n}\n\nfragment photoResult on PhotoResult {\n  result\n  llsid\n  expTag\n  serverExpTag\n  pcursor\n  feeds {\n    ...feedContent\n    __typename\n  }\n  webPageArea\n  __typename\n}\n\nquery brilliantTypeDataQuery($pcursor: String, $hotChannelId: String, $page: String, $webPageArea: String) {\n  brilliantTypeData(pcursor: $pcursor, hotChannelId: $hotChannelId, page: $page, webPageArea: $webPageArea) {\n    ...photoResult\n    __typename\n  }\n}\n"}
        r = requests.post(url=self.url, headers=self.headers, json=data)
        r.encoding = "utf-8"
        for feed in  json.loads(r.text)['data']['brilliantTypeData']['feeds']:
            yield feed

    def getDate(self):
        pass

    def main(self):
        """

        """
        for feed in list(self.getFeeds())[:3]:
            item = defaultdict(str)
            # print(feed)
            # 作者姓名 标题 点赞 评论 作品 粉丝 关注
            item['authorName'] = feed['author']['name']
            item['title'] = feed['photo']['caption']
            item['realLikeCount'] = feed['photo']['realLikeCount']
            item['commentCount'] = self.getComment(feed['photo']['id'])
            ownerCount = self.homePage(feed['author']['id'])
            item['photoPublic'] = ownerCount['photo_public']
            item['fan'] = ownerCount['fan']
            item['follow'] = ownerCount['follow']
            # 链接地址
            item['url'] = '{}/{}'.format(self.videoUrl, feed['photo']['id'])
            item['authorUrl'] = '{}/{}'.format(self.authorUrl, feed['author']['id'])
            item['source'] = '快手'
            item['id'] = feed['photo']['id']
            item['time'] = time.strftime("%Y-%m-%d", time.localtime())

            print(item)


if __name__ == '__main__':
    ks = Kuaishou()
    ks.main()