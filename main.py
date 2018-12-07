
import json
import requests
import re
from mitmproxy import ctx
import time
from settings import VIDEOPATH,STARTID
from db import login_mongodb

class DownloadHot():
    """
    response(flow)实现了对抖音APP请求的处理.
    """
    def __init__(self):
        """
        初始化了运行log的输出；视频和文本的本地路径；动态存储所有文本的字典；文本和视频的计数.
        """
        self.info = ctx.log.info
        self.__videopath = VIDEOPATH+'NO.{count}-{desc}.mp4'
        self.__data = {}
        self.__video_count=STARTID
        self.__info_count =STARTID


    def test(self,text):
        self.__get_info(text)

    def __get_info(self, text):
        """
        解析出多条文本信息，包括视频帖内容，点赞和评论的数目，发布时间，作者的id等信息;
        保存到mongodb;
        更新文档的计数.
        :param text:response的内容
        :return:None
        """
        self.info('start getting text----------')
        data = json.loads(text)
        objects = data.get('aweme_list')
        for object in objects:
            statistics = object['statistics']
            self.__data[self.__info_count] = {
                'id':'NO.'+str(self.__info_count),
                'desc': object['desc'],
                'author':object['author']['nickname'],
                'author_id':object['author']['short_id'],
                'create_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(object['create_time'])),
                'music_title': object['music']['title'],
                'music_author': object['music']['author'],
                'aweme_id': statistics['aweme_id'],
                'comment_count': statistics['comment_count'],
                'digg_count': statistics['digg_count'],
                'play_count': statistics['play_count'],
                'share_count': statistics['share_count'],
                'forward_count': statistics['forward_count']
            }
            self.info(str(self.__data[self.__info_count]))
            self.db=login_mongodb()
            try:
                self.db.insert(self.__data[self.__info_count])
            except:
                self.info('error:id has been in mongodb')

            self.__info_count = self.__info_count + 1


    def __get_video(self, url):
        """
        视频链接存入mongodb;
        视频保存到本地,视频命名为 NO.+视频数目+视频帖内容;
        更新视频数量.
        :param url:视频的链接
        :return:None
        """
        self.info('start getting video-----------')
        video_info = self.__data.pop(self.__video_count)
        video = requests.get(url, stream=True)

        self.db=login_mongodb()
        self.db.update_one({"id": {"$regex": 'NO.' + str(self.__video_count)}}, {"$set": {"url": url}})

        with open(self.__videopath.format(count=self.__video_count,desc=video_info['desc']), 'ab') as f:
            f.write(video.content)
            f.flush()
            self.info('视频存储成功')

        self.__video_count = self.__video_count + 1


    def response(self, flow):
        """
        根据请求状态过滤链接;
        正则表达式过滤文本链接，符合则开始处理文本信息;
        正则表达式过滤视频链接，符合则开始处理视频信息.
        :param flow:
        :return:
        """
        req = flow.request
        res = flow.response
        url = req.url
        if res.status_code in [200, 206]:

            filter0 = re.match(r'https://.*?eagle.*?.com/aweme/v1/feed/.*', url, re.S)
            if filter0:
                self.__get_info(text=res.text)

            filter1 = re.match(r'http://\d+.\d+.\d+.*?ixigua.com.*?video/m.*', url, re.S)
            filter2 = re.match(r'http://.*v\d-dy.*?ixigua.com.*?video/m.*', url, re.S)
            if filter1 or filter2:
                self.__get_video(url=url)


addons = [
    DownloadHot()
]






