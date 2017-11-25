#! /usr/bin/env python
# coding:utf-8
# author:jzh
# 时间：2015-10-14 10:17


import utils, traceback


def get_schedule_pubnum_id(db):
    return db.query("select pubnum_id from wechat_pubnum where last_article_time > %(article_time)s",
                    article_time=utils.get_middle_night())


def set_pubnum_status(db, pubnum_id, stauts=0):
    return db.update("update wechat_pubnum set status=%(status)s where pubnum_id=%(pubnum_id)s",
                     pubnum_id=pubnum_id, stauts=stauts)


def push_pubnum_to_crawler(db, pubnum_id):
    return set_pubnum_status(db, pubnum_id)


def set_pubnum_to_disable(db, pubnum_id):
    return set_pubnum_status(db, pubnum_id, stauts=2)


def set_pubnum_to_crawlered(db, pubnum_id):
    return set_pubnum_status(db, pubnum_id, stauts=1)


def get_pubnum_by_status(db, status):
    return db.query("select pubnum_id, originid, biz from wechat_pubnum where status=%(status)s",
                    status=status)


def get_wechat_key(db):
    return db.get("select * from wechat_key limit 1")


def insert_wechat_key(db, wechat_key):
    return db.insert("insert into wechat_key(content) values(%(content)s)",
                     content=wechat_key)


def update_wechat_key(db, wechat_key):
    return db.update("update wechat_key set content=%(content)s",
                     content=wechat_key)


def upsert_wechat_key(db, key_content):
    record = get_wechat_key(db)
    if not record:
        return insert_wechat_key(db, key_content)
    return update_wechat_key(db, key_content)


def get_wechat_article_by_url_md5(db, url_md5):
    return db.get('select * from wechat_article where url_md5=%(url_md5)s',
                  url_md5=url_md5)


def update_pubnum_article_time(db, pubnum_id, article_time):
    return db.update("update wechat_pubnum set last_article_time=%(art_time)s where pubnum_id=%(pubnum_id)s",
                     pubnum_id=pubnum_id, article_time=article_time)

def save_article(db, pubnum_id, art):
    try:
        return db.insert("insert into wechat_article(pubnum_id, url_md5, content_url, title, "
                         "author, cover_url, publish_time, create_time) values (%(pubnum_id)s, %(url_md5)s, "
                         "%(content_url)s, %(title)s, %(author)s, %(publish_time)s, %(create_time)s)",
                         pubnum_id=pubnum_id, url_md5=art['url_md5'], content_url=art['content_url'],
                         title=art['title'], author=art['author'], conver_url=art['conver_url'],
                         publish_time=art['publish_time'], create_time=utils.get_curr_time())
    except Exception as e:
        print traceback.format_exc()
        return False


def save_wecaht_pubnum(db, p):
    try:
        return db.insert('insert into wechat_pubnum(wechat_name, nick_name, pic_url,qr_code, originid, '
                     'biz, status, create_time) values(%(wechat_name)s, %(nick_name)s, %(pic_url)s, '
                     '%(qr_code)s, %(originid)s, %(biz)s, 0, %(curr_time)s);',
                     wechat_name=p.get('originid', ''), nick_name=p.get('nick_name',''),
                     pic_url=p.get('pic_url', ''), qr_code=p.get('qr_code', ''),
                     originid=p.get('originid', ''), biz=p.get('biz', ''), curr_time=utils.get_curr_time())
    except Exception as e:
        print traceback.format_exc()
        return False








