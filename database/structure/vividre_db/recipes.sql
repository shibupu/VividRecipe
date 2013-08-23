CREATE TABLE `recipes` (
  `recipe_id` int(10) unsigned NOT NULL auto_increment,
  `user_id` int(11) NOT NULL default '0',
  `name` varchar(255) NOT NULL default '',
  `style` varchar(255) default NULL,
  `category` varchar(255) default NULL,
  `image` varchar(255) default NULL,
  `description` text,
  `ingredients` text,
  `top_ten_recipe` tinyint(4) NOT NULL default '0',
  `todays_recipe` tinyint(4) NOT NULL default '0',
  `easy_recipe` tinyint(4) NOT NULL default '0',
  `added_date` timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (`recipe_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
