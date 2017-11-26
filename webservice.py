#! /usr/bin/env python
# coding:utf-8
# author:jzh
import tornado.ioloop, dao, extractor, traceback, db
import tornado.web, conf, utils
from log import Log
mydqldb = db.Connection(host=conf.MYSQL_HOST, user=conf.MYSQL_USER,
                        password=conf.MYSQL_PASSWD, database=conf.MYSQL_DB,
                        time_zone='+8:00', max_idle_time=252)
weblog = Log("./logs", name="web-log", dividelevel=0, loglevel="info")


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            article_url = self.get_argument('url', '')
            weblog.info('article url %s ' % article_url)
            if not article_url:
                return self.write({'status': 1, 'message': 'no url params'})
            content = utils.get_content(article_url)
            article = extractor.parse_pubnum_from_article(content)
            weblog.info('extrat article info %s ' % article)
            if not article or 'biz' not in article or 'originid' not in article:
                return self.write({'status': 1, 'message': 'parse pubnum error!'})
            pubnum = dao.get_pubnum_by_originid(mydqldb, article['originid'])
            if pubnum:
                return self.write({'status': 1, 'message': 'pubnum exists!'})
            status = dao.save_wecaht_pubnum(mydqldb, article)
            weblog.info('save wecaht pubnum status: %s' % status)
            if status is False:
                return self.write({'status': 1, 'message': 'write pubnum error!!'})
            self.write({'status': 0, 'message': 'success!'})
        except Exception as e:
            self.write({'status': 1, 'message': traceback.format_exc()})
            weblog.error(traceback.format_exc())


def make_app():
    return tornado.web.Application([
        (r"/parse_article", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    weblog.info('start server listen on %s' % conf.PUBNUM_ADD_WEB_PORT)
    app.listen(conf.PUBNUM_ADD_WEB_PORT)
    tornado.ioloop.IOLoop.current().start()


