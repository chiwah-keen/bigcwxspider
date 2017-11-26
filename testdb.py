#! /usr/bin/env python
# coding:utf-8
# author:jzh
import tornado.ioloop, dao, extractor, traceback, db
import tornado.web, conf, utils
from log import Log
mydqldb = db.Connection(host=conf.MYSQL_HOST, user=conf.MYSQL_USER,
                        password=conf.MYSQL_PASSWD, database=conf.MYSQL_DB,
                        time_zone='+8:00', max_idle_time=252)

print mydqldb.query("select * from wechat_key;")

