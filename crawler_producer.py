#! /usr/bin/env python
# coding:utf-8
# author:jzh
# 时间：2015-10-14 10:17


import conf, db, multiprocessing, dao, traceback, time
from log import Log


class QueueProducer(multiprocessing.Process):

    def __init__(self, queue):
        multiprocessing.Process.__init__(self)
        self.log = Log("./logs", name="producer-queue.log", dividelevel=0, loglevel="info")
        self.queue = queue
        self.mydqldb = db.Connection(host=conf.MYSQL_HOST, user=conf.MYSQL_USER,
                                     password=conf.MYSQL_PASSWD, database=conf.MYSQL_DB,
                                     time_zone='+8:00', max_idle_time=252)

    def get_uncrawl_pubnum(self):
        return dao.get_pubnum_by_status(self.mydqldb, 0)

    def run(self):
        while True:
            try:
                pubnums = self.get_uncrawl_pubnum()
                self.log.info('----- start to push pubnum to queue len %s-----' % len(pubnums))
                for pubnum in pubnums:
                    if not pubnum.biz:
                        self.log.error('current pubnum has no biz %s ' % pubnum)
                        continue
                    self.log.info(' push pubnum to queue, pub info : %s' % pubnum)
                    self.queue.put(pubnum)
                self.log.info('-----  end to push pubnum to queue -----')
                time.sleep(conf.PUSH_QUEUE_SUCCESS_TIMESCALE)
            except Exception as e:
                self.log.error(traceback.format_exc())
                time.sleep(conf.PUSH_QUEUE_FAILED_TIMESCALE)
