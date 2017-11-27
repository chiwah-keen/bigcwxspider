#! /usr/bin/env python
# coding:utf-8
# author:jzh

import db, conf, utils, dao
from log import Log


class schedulePush(object):

    def __init__(self):
        self.log = Log('./logs', 'schedule-push.log', dividelevel=0, loglevel="info")
        self.mydqldb = db.Connection(host=conf.MYSQL_HOST, user=conf.MYSQL_USER,
                                     password=conf.MYSQL_PASSWD, database=conf.MYSQL_DB,
                                     time_zone='+8:00', max_idle_time=252)

    # main func here.
    def start(self):
        pubnums = dao.get_schedule_pubnum_id(self.mydqldb)
        self.log.info('----- start to push pubnum to crawler crawler num: %s-----' % (len(pubnums)))
        for pubnum in pubnums:
            status = dao.push_pubnum_to_crawler(self.mydqldb, pubnum.pubnum_id)
            self.log.info('push pubnum to crawler %s %s ' % (str(pubnum), 0))
        self.log.info('----- end to push pubnum to crawler -----')
        self.mydqldb.close()

pusher = schedulePush()
pusher.start()