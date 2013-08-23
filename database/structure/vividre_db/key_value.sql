CREATE TABLE `key_value` (
  `key_field` varchar(50) NOT NULL default '',
  `value_field` bigint(20) NOT NULL default '1',
  PRIMARY KEY  (`key_field`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 CHECKSUM=1 DELAY_KEY_WRITE=1 ROW_FORMAT=DYNAMIC;

insert  into `key_value`(`key_field`,`value_field`) values ('session_login_id',1);
