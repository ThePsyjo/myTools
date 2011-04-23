-- Table template
CREATE TABLE `apachelog` (
  `datetime` datetime DEFAULT NULL,
  `filename` text,
  `requestmethod` varchar(8) DEFAULT NULL,
  `remote_ip` varchar(15) DEFAULT NULL,
  `remote_user` varchar(128) DEFAULT NULL,
  `site` varchar(64) DEFAULT NULL,
  `host` varchar(64) DEFAULT NULL,
  `url` text,
  `status` smallint(6) NOT NULL,
  `bytes_sent` int(10) unsigned DEFAULT NULL,
  `bytes_received` int(10) unsigned DEFAULT NULL,
  `delay` int(10) unsigned DEFAULT NULL,
  `referer` text,
  `content_type` varchar(32) DEFAULT NULL,
  `seq` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  KEY `seq` (`seq`),
  KEY `site` (`site`),
  KEY `host` (`host`),
  KEY `datetime` (`datetime`)
) ENGINE=MyIsam DEFAULT CHARSET=utf8
PARTITION BY RANGE (TO_SECONDS(datetime))
(
PARTITION p999999999999 VALUES LESS THAN MAXVALUE
);

-- p999999999999 == max partition name for p%y%m%d%H%i%S
-- (1 second granularity)


-- insert from apache
INSERT INTO apachelog (datetime, filename, requestmethod, remote_ip, remote_user, site, host, url, status, bytes_sent, bytes_received, delay, referer, content_type)\
        VALUES ('%{%Y-%m-%d %H:%M:%S}t', '%f', '%m', '%a', '%u', '%{Host}i', '%v', '%U%q', '%s', '%B', '%I', '%D', '%{Referer}i', '%{Content-Type}o');
