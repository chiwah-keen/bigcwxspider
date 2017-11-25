# create table wechat key
DROP TABLE IF EXISTS wechat_key;
CREATE TABLE `wechat_key` (
 `key_id` int(32) NOT NULL AUTO_INCREMENT COMMENT 'id',
 `content` mediumblob COMMENT 'key content, json type',
 `last_update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
 PRIMARY KEY (`key_id`)
) ENGINE=InnoDB AUTO_INCREMENT=104966 DEFAULT CHARSET=utf8;


# create table wechat_pubnum
DROP TABLE IF EXISTS wechat_pubnum;
CREATE TABLE `wechat_pubnum` (
 `pubnum_id` int(32) NOT NULL AUTO_INCREMENT COMMENT 'id',
 `wechat_name` varchar(128) DEFAULT '' COMMENT '公众号id',
 `nick_name` varchar(128) DEFAULT '' COMMENT '公众号名称',
 `pic_url` varchar(256) DEFAULT '' COMMENT '公众号头像',
 `qr_code` varchar(256) DEFAULT '' COMMENT '公众号二维码',
 `originid` varchar(256) DEFAULT '' COMMENT '公众号微信识别码',
 `biz` varchar(256) DEFAULT '' COMMENT '公众号抓取识别码',
 `status` int(4) DEFAULT '0' COMMENT '公众号状态: 0, 待抓取， 1， 已抓取， 2，无效',
 `last_article_time`  timestamp NOT NULL DEFAULT '0000-00-00 00:00:00' COMMENT '最后一次发文时间',
 `create_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00' COMMENT '创建时间',
 `last_update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
 PRIMARY KEY (`pubnum_id`)
) ENGINE=InnoDB AUTO_INCREMENT=104966 DEFAULT CHARSET=utf8;

# create table wechat_article
DROP TABLE IF EXISTS wechat_article;
CREATE TABLE `wechat_article` (
 `article_id` int(32) NOT NULL AUTO_INCREMENT COMMENT 'id',
 `pubnum_id` int(32) NOT NULL COMMENT 'wechat_pubnum.id',
 `url_md5` varchar(128) DEFAULT '' COMMENT '文章url md5' ,
 `content_url` varchar(1024) DEFAULT '' COMMENT '文章url',
 `title` varchar(128) DEFAULT '' COMMENT '文章标题',
 `author` varchar(128) DEFAULT '' COMMENT '作者名',
 `cover_url` varchar(1024) DEFAULT '' COMMENT '头图url',
 `publish_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00' COMMENT '发文时间',
 `create_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00' COMMENT '创建时间',
 `last_update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
 PRIMARY KEY (`article_id`),
 KEY `url_md5` (`url_md5`)
) ENGINE=InnoDB AUTO_INCREMENT=104966 DEFAULT CHARSET=utf8;

