#! /usr/bin/env python
# coding:utf-8
# author:jzh
# 时间：2015-10-14 10:17


import conf, db, multiprocessing, traceback, time, dao, utils, json, sys
import HTMLParser
from log import Log
from crawler_weixin import CrawlerWeixin


class QueueConsumer(multiprocessing.Process):

    def __init__(self, idx, queue):
        multiprocessing.Process.__init__(self)
        self.log = Log("./logs", name="consumer-%s-log" % idx, dividelevel=0, loglevel="debug")
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
                self.log.info('get pubnum info %s' % self.pubnum)
                return self.pubnum
            except Exception as e:
                self.log.info('get error %s' % e)
                self.log.error(traceback.format_exc())
                time.sleep(conf.POP_QUEUE_FAILED_TIMESCALE)

    def update_key_from_api(self):
        content = utils.get_content(conf.GET_KEY_API)
        keys_record = utils.json_loads(content)
        if not keys_record:
            self.log.error('get keys from api failed %s' % keys_record)
            return False
        dao.upsert_wechat_key(self.mydqldb, json.dumps(keys_record))
        return True

    def get_wechat_key(self):
        if self.wechat_key and int(time.time()) - self.last_wechat_key_time < conf.WECHAT_KEY_TTL:
            return self.wechat_key
        if int(self.idx) == 0:
            self.update_key_from_api()
        wechat_record = dao.get_wechat_key(self.mydqldb)
        if int(time.time()) - utils.get_timestamp(str(wechat_record.last_update_time)) > conf.WECHAT_KEY_TTL:
            self.log.info('sleep 10 seconds indx: %s' % self.idx)
            time.sleep(10)
            return self.get_wechat_key()
        if not wechat_record:
            self.log.error('get wechat key error! %s ' % wechat_record)
            return None
        response_info = utils.json_loads(wechat_record.content)
        wechat_keys = response_info.get('data')
        self.wechat_key = wechat_keys[self.idx]
        return self.wechat_key

    def parse_article_common(self, art):
        wechat_article = dict()
        wechat_article['author'] = art.get('author', '')
        wechat_article['cover_url'] = HTMLParser.HTMLParser().unescape(art.get('cover', '').replace("\\", ''))
        wechat_article['content_url'] = HTMLParser.HTMLParser().unescape(art.get('content_url', '').replace("\\", ''))
        wechat_article['title'] = art.get('title', '')
        wechat_article['url_md5'] = utils.sign_url(wechat_article['content_url'])
        return wechat_article

    def parse_articles(self, articles_list):
        all_articles = []
        for articles in articles_list:
            article_timestamp = articles.get('comm_msg_info', {}).get('datetime')
            article_time = utils.get_format_time(article_timestamp)
            wechat_article = self.parse_article_common(articles.get('app_msg_ext_info'))
            wechat_article['publish_time'] = article_time
            all_articles.append(wechat_article)
            for art in articles.get('app_msg_ext_info', {}).get('multi_app_msg_item_list', []):
                wechat_article = self.parse_article_common(art)
                wechat_article['publish_time'] = article_time
                all_articles.append(wechat_article)
        return all_articles

    def save_articles(self, pubnum_id, articles):
        for art in articles:
            article = dao.get_wechat_article_by_url_md5(self.mydqldb, art['url_md5'])
            if article:
                self.log.info('article has been saved ...url md5 %s' % art['url_md5'])
                continue
            dao.save_article(self.mydqldb, pubnum_id, art)

    def get_last_update_time(self, articles):
        last_update_time = ''
        for a in articles:
            if last_update_time < a['publish_time']:
                last_update_time = a['publish_time']
        return last_update_time

    def run(self):
        while True:
            try:
                pubnum = self.get_pubnum()
                if not pubnum:
                    continue
                key = self.get_wechat_key()
                if not key:
                    time.sleep(conf.GET_NO_WECHAT_KEY_TIMESCALE)
                    continue
                biz = pubnum.biz
                uin = key.get('uin')
                key = key.get('key')
                pass_ticket = ''
                self.log.info('start to crawle wechat article list biz:%s uin:%s key:%s' % (biz, uin, key))
                articles_list = self.craler_handler.get_news_list(biz, uin, key, pass_ticket)
                self.log.info('article list %s' % articles_list)
                if not articles_list:
                    time.sleep(conf.GET_NO_WECHAT_KEY_TIMESCALE)
                    continue
                articles = self.parse_articles(articles_list)
                self.log.info(articles)
                self.save_articles(pubnum.pubnum_id, articles)
                last_update_time = self.get_last_update_time(articles)
                dao.update_pubnum_article_time(self.mydqldb, pubnum.pubnum_id, last_update_time)
                dao.set_pubnum_to_crawlered(self.mydqldb, pubnum.pubnum_id)
                self.pubnum = None  # 设置为成功
                time.sleep(1)
            except Exception as e:
                self.log.error(traceback.format_exc())
                time.sleep(conf.CONSUMER_ERROR_TIMESCALE)


