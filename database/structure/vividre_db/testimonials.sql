CREATE TABLE `testimonials` (
  `testimonial_id` int(10) unsigned NOT NULL auto_increment,
  `user_id` int(11) NOT NULL default '0',
  `testimonial` text,
  `added_date` timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (`testimonial_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
