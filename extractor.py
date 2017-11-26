#! /usr/bin/env python
# coding:utf-8
# author:jzh
import traceback, re
from log import Log
extratorlog = Log("./logs", name="extractor-log", dividelevel=0, loglevel="info")


RE_MSGLIST = re.compile(r'\s*msgList =\s*(.*);')
RE_PUBNUM_NICK_NAME = re.compile(r'\s*var nickname = "(.*)";')
RE_PUBNUM_WCHAT_NAME = re.compile(r'\s*var user_name = "(.*)";')
RE_PUBNUM_PIC_URL = re.compile(r'\s*var round_head_img = "(.*)";')
RE_PUBNUM_ORIGINID = re.compile(r'\s*var user_name = "(.*)";')
RE_PUBNUM_BIZ = re.compile(r'\s*var\s*appuin\s*=\s*"(.*)"\|\|"(.*)";')


def parse_pubnum_from_article(content):
    if not content: return {}
    article = {}
    try:
        nick_name = RE_PUBNUM_NICK_NAME.search(content)
        nick_name = nick_name.group(1) if nick_name else ''
        wchat_name = RE_PUBNUM_WCHAT_NAME.search(content)
        wchat_name = wchat_name.group(1) if wchat_name else ''
        pic_url = RE_PUBNUM_PIC_URL.search(content)
        pic_url = pic_url.group(1) if pic_url else ''
        originid = RE_PUBNUM_ORIGINID.search(content)
        originid = originid.group(1) if originid else ''
        biz = RE_PUBNUM_BIZ.search(content)
        biz = biz.group(1) if biz and biz.group(1) else (biz.group(2) if biz.group(2) else '')
        article['nick_name'] = nick_name
        article['wchat_name'] = wchat_name
        article['pic_url'] = pic_url
        article['originid'] = originid
        article['biz'] = biz
        return article
    except Exception as e:
        extratorlog.error(traceback.format_exc())
        return None

if __name__ == "__main__":
    biz = RE_PUBNUM_BIZ.search("""  var appuin = ""||"MzA4MTY2ODUwMA==";  """)
    biz = biz.group(1) if biz and biz.group(1) else (biz.group(2) if biz.group(2) else '')
    print biz


