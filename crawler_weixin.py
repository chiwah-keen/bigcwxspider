#! /usr/bin/env python
# coding:utf-8
# author:wenhui
# 时间：2015-10-14 10:17

import time, random, sys, traceback, utils
from log import Log
import requests, re, urllib
import HTMLParser
import logging

reload(sys)
sys.setdefaultencoding('utf8')

RE_ERRMSG = re.compile(r'class="weui_msg_desc">(.*)</p>')
RE_MSGLIST = re.compile(r'\s*msgList =\s*(.*);')
RE_APPMSGTOKEN = re.compile(r".*appmsg_token\s*=\s*\"(.*)\";")

log = logging.getLogger(__name__)

HEADERS = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_2_1 like Mac OS X) '
                         'AppleWebKit/602.4.6 (KHTML, like Gecko) Mobile/14D27 '
                         'MicroMessenger/6.5.4 NetType/WIFI Language/zh_CN'}


class CrawlerWeixin(object):

    def __init__(self):
        self.log = Log("./logs", name="craler-weixin", dividelevel=0, loglevel="info")
        self.headers = HEADERS

    def parse_article_list(self, content):
        rst = RE_MSGLIST.search(content)
        html_parser = HTMLParser.HTMLParser()
        article_list =  html_parser.unescape(rst.group(1)) if rst else None
        mrst = RE_APPMSGTOKEN.search(content)
        msg_token = mrst.group(1) if mrst else ''
        return article_list, msg_token

    def get_news_list(self, biz, uin, key, pass_ticket='', frommsgid=''):
        # 获取公众号文章列表
        msgsend_url = "https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=%s&scene=124&" \
                      "devicetype=android-22&version=26050732&lang=zh_CN&nettype=" \
                      "WIFI&a8scene=3&pass_ticket=%s&wx_header=1 " %(biz, pass_ticket)
        try:
            if not hasattr(self, 'cookies'):
                self.cookies = {}
            if not hasattr(self, 'wxparams'):
                self.wxparams = {}
            time.sleep(random.randint(5, 10))
            # print cookies
            self.headers['X-WECHAT-KEY'] = key
            self.headers['X-WECHAT-UIN'] = urllib.quote(uin)
            content = utils.get_content(msgsend_url, cookies=self.cookies, headers=self.headers, verify=False)
            #  set cookies.
            if not content:
                self.log.warn('get new list failed, biz=%s, errmsg=response error %s ' % (biz, uin))
                return []
            news_json, msg_token = self.parse_article_list(content)
            if msg_token:
                self.wxparams['appmsg_token'] = msg_token
            if not news_json:
                r = re.search(RE_ERRMSG, content)
                self.log.warn(content)
                self.log.warn("parse no article list biz %s, uin %s, errmsg: %s" % (biz, uin, r.group(1) if r else ''))
                #  如果出现页面无法打开， api中的uin不能使用。
                if '<h2 class="weui_msg_title">页面无法打开</h2>' in content \
                        or '<p>请在微信客户端打开链接。</p>' in content \
                        or '<h2 class="weui_msg_title">操作频繁，请稍后再试</h2>' in content:
                    return []
            news_json = news_json.strip()
            if news_json.startswith("'"):
                news_json = news_json[1:-1]
            news_json = utils.json_loads(news_json)
            if not news_json:
                self.log.warn('failed to loads json, biz=%s, uin=%s' % (biz, uin))
                return []
            self.log.info("crawl news list success len:%s" % len(news_json.get('list', [])))
            return news_json.get('list', [])
        except Exception as e:
            self.log.error('get news list Exception:%s, biz:%s, uin:%s' % (traceback.format_exc(), biz, uin))
            return []


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == 'test_list':
        inst = CrawlerWeixin('')
        biz = ''
        uin = ''
        key = ''
        print inst.get_news_list(biz, uin, key)
