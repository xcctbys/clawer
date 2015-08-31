use todo;

#alter table todo_userprofile drop last_feed_datetime;

/* you must create superuser admin:admin */
/*
insert into todo_userprofile \
	(`user_id`, 
	`nickname`, 
	`tomato_number`, 
	`tomato_used_number`, 
	`in_black_house`, 
	`come_from`, 
	`last_upload_header_datetime`, 
	`tomato_rollcall_number`, 
	`tomato_dead_number`, 
	`experience`, 
	`level`, 
	`place`,
    `register_ip`) values (1, 'good', 0, 0, false, 'china', null, 3, 0, 0, 0, "bj", "127.0.0.1");
*/
	
update auth_user set is_superuser = 1;
update auth_user set is_staff = 1;
insert into django_site (`domain`, `name`) values ('http://www.baidu.com', "baidu");

