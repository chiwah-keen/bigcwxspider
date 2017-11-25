#! /usr/bin/env python
# coding:utf-8
# author:jzh

import time, json, traceback, requests, random, urlparse, hashlib
from log import Log
utilslog = Log("../logs", name="utils-log", dividelevel=0, loglevel="info")

dheaders = {
    'User-Agent' : 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) '
                   'AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 '
                   'Safari/601.1',
    'Host': 'mp.weixin.qq.com'

}


def get_middle_night(days=0, fmt="%Y-%m-%d 00:00:00"):
    t = (int(time.time()) / 86400 + days) * 86400
    return time.strftime(fmt, time.localtime(float(t)))


def get_curr_time(fmt='%Y-%m-%d %H:%M:%S'):
    return time.strftime(fmt)


def get_timestamp(t=time.time(), fmt="%Y-%m-%d %H:%M:%S", getint=True):
    if isinstance(t, (int, float)) or str(t).replace('.', '', 1).isdigit():
        return int(t) if getint else t
    if isinstance(t, basestring):
        t = time.mktime(time.strptime(t, fmt))
        return int(t) if getint else t
    if isinstance(t, time.struct_time):
        t = time.mktime(t)
        return int(t) if getint else t


def json_loads(json_str):
    try:
        return json.loads(json_str)
    except Exception as e:
        utilslog.error(traceback.format_exc())
        return None


def get_content(url, max_try=10, verify=True, headers={}):
    while max_try:
        try:
            headers = headers or dheaders
            r = requests.get(url, headers=headers, timeout=20, verify=verify)
            if r.status_code != requests.codes.ok:
                utilslog.error("requests code error %s, url %s" % (r.status_code, url))
                max_try -= 1
                time.sleep(random.randint(3, 50))
                continue
            return r.content
        except Exception as e:
            utilslog.error(traceback.format_exc())
            max_try -= 1
            time.sleep(3)
            continue
    return None


def sign_url(url):
    pure_url = url.replace('?' + urlparse.urlparse(url).query, '')
    url_params = dict(urlparse.parse_qsl(urlparse.urlsplit(url).query))
    url_keys = url_params.keys()
    url_keys.sort()
    params = []
    for k in url_keys:
        params.append(k + "=" + url_params.get(k))
    sorted_url = pure_url + "?" + "&".join(params)
    m = hashlib.md5()
    m.update(sorted_url)
    return m.hexdigest()


if __name__ == "__main__":
    print get_middle_night(days=-1)

