#! /usr/bin/env python
# coding:utf-8
# author:jzh
# 时间：2015-10-14 10:17


import conf, db, multiprocessing, traceback, time, dao, utils, json

from log import Log
from crawler_weixin import CrawlerWeixin


class QueueConsumer(multiprocessing.Process):

    def __init__(self, idx, queue):
        multiprocessing.Process.__init__(self)
        self.log = Log("../logs", name="main-log", dividelevel=0, loglevel="info")
        self.idx = idx
        self.queue = queue
        self.wechat_key = None
        self.pubnum = None
        self.last_wechat_key_time = int(time.time())
        self.craler_handler = CrawlerWeixin()
        self.mydqldb = db.Connection(host=conf.MYSQL_HOST, user=conf.MYSQL_USER,
                                     password=conf.MYSQL_PASSWD, database=conf.MYSQL_DB,
                                     time_zone='+8:00', max_idle_time=252)

    def get_pubnum(self):
        while True:
            try:
                if self.pubnum: return self.pubnum
                self.pubnum = self.queue.get()
                return self.pubnum
            except Exception as e:
                self.log.error(traceback.format_exc())
                time.sleep(conf.POP_QUEUE_FAILED_TIMESCALE)

    def update_key_from_api(self):
        content = utils.get_content(conf.GET_KEY_API)
        keys_record = utils.json_loads(content)
        if not keys_record:
            self.log.error('get keys from api failed %s' % keys_record)
            return False
        dao.upsert_wechat_key(json.dumps(keys_record))
        return True

    def get_wechat_key(self):
        if int(time.time()) - self.last_wechat_key_time < conf.WECHAT_KEY_TTL:
            return self.wechat_key
        if int(self.idx) == 0:
            self.update_key_from_api()
        wechat_record = dao.get_wechat_key(self.mydqldb)
        if int(time.time()) - utils.get_timestamp(str(wechat_record.last_update_time)) > conf.WECHAT_KEY_TTL:
            self.log.info('sleep 10 seconds indx: %s' % self.idx)
            time.sleep(10)
            return self.get_wechat_key()
        wechat_keys = utils.json_loads(wechat_record.content)
        if not wechat_record :
            self.log.error('get wechat key error! %s ' % wechat_record)
            return None
        self.wechat_key = wechat_keys[self.idx]
        return self.wechat_key

    def save_articles(self, pubnum_id, articles_list):
        last_article_time = ''
        for articles in articles_list:
            article_time = articles.get('datetime')
            if article_time > last_article_time:
                last_article_time = article_time
            for art in articles.get('articles'):
                wechat_article = {}
                wechat_article['article_time'] = article_time
                wechat_article['author'] = art.get('author', '')
                wechat_article['cover_url'] = art.get('cover_url', '')
                wechat_article['content_url'] = art.get('content_url', '')
                wechat_article['title'] = art.get('title', '')
                wechat_article['url_md5'] = utils.sign_url(wechat_article['content_url'])
                article = dao.get_wechat_article_by_url_md5(wechat_article['url_md5'])
                if article:
                    self.log.info('article has been saved... url md5 %s' % wechat_article['url_md5'])
                    continue
                self.log.info('will save wechat ariticle url md5 %s' % wechat_article['url_md5'])
                dao.save_article(self.mydqldb, pubnum_id, wechat_article)
        return last_article_time

    def run(self):
        while True:
            pubnum = self.get_pubnum()
            key = self.get_wechat_key()
            if not key:
                time.sleep(conf.GET_NO_WECHAT_KEY_TIMESCALE)
                continue
            biz, uin, key, pass_ticket = self.wechat_key
            articles_list = self.craler_handler.get_news_list()
            if not articles_list:
                time.sleep(conf.GET_NO_WECHAT_KEY_TIMESCALE)
                continue
            last_update_time = self.save_articles(pubnum.pubnum_id, articles_list)
            dao.update_pubnum_article_time(self.mydqldb, pubnum.pubnum_id, last_update_time)


