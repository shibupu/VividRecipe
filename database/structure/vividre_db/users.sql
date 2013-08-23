CREATE TABLE `users` (
  `user_id` int(10) unsigned NOT NULL auto_increment,
  `email` varchar(255) NOT NULL default '',
  `password` varchar(255) NOT NULL default '',
  `name` varchar(255) default NULL,
  `address` varchar(255) default NULL,
  `place` varchar(255) default NULL,
  `city` varchar(255) default NULL,
  `state` varchar(255) default NULL,
  `pin` varchar(20) default NULL,
  `phone` varchar(20) default NULL,
  `added_date` timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (`user_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
