CREATE TABLE `session` (
  `row_no` int(10) unsigned NOT NULL auto_increment,
  `user_id` varchar(50) NOT NULL default '',
  `session_login_id` bigint(20) unsigned NOT NULL default '0',
  `session_id` varchar(35) NOT NULL default '',
  `session_time` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  PRIMARY KEY  (`row_no`),
  KEY `user_id` USING HASH (`user_id`),
  KEY `session_login_id` USING HASH (`session_login_id`)
) ENGINE=HEAP DEFAULT CHARSET=latin1;
