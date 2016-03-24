#!/usr/bin/python
#coding:utf8
import sys
import MySQLdb

db_total_list = []
db_down_list = []
def get_total_dict_from_db():
	try:
		conn = MySQLdb.connect(host='10.100.80.50', user='cacti', passwd='cacti', db='clawer', port=3306)
		cur = conn.cursor()
		count = cur.execute('select register_no from enterprise_enterprise')
		results = cur.fetchall()
		for result in results:
			# print result
			if result[0]:
				try:
					db_total_list.append(result[0].strip())
				except KeyError as e:
					pass
		# print results
		cur.close()
		conn.close()
	except MySQLdb.Error, e:
		print 'Mysql error %d:%s' %(e.args[0], e.args[1])

def get_down_dict_from_db():
	try:
		conn = MySQLdb.connect(host='10.100.80.50', user='cacti', passwd='cacti', db='enterprise', port=3306)
		cur = conn.cursor()
		count = cur.execute('select register_num from basic')
		results = cur.fetchall()
		for result in results:
			if result[0]:
				try:
					db_down_list.append(result[0].strip())
				except KeyError as e:
					pass
		cur.close()
		conn.close()
	except MySQLdb.Error, e:
		print 'Mysql error %d:%s' %(e.args[0], e.args[1])

def update_db_clawertask():
	try:
		conn = MySQLdb.connect(host='10.100.80.50', user='cacti', passwd='cacti', db='clawer', port=3306)
		cur = conn.cursor()
		count = cur.execute('delete from clawer_clawertask as task where task.clawer_id=7 and task.status=1')
		conn.commit()
		count = cur.execute('delete clawer_clawerdownloadlog from clawer_clawertask, clawer_clawerdownloadlog where clawer_clawerdownloadlog.task_id = clawer_clawertask.id and clawer_clawertask.clawer_id=7 and clawer_clawertask.status=2')
		conn.commit()
		count = cur.execute('delete clawer_clawertask from clawer_clawertask where clawer_clawertask.clawer_id=7 and clawer_clawertask.status=2')
		conn.commit()
		cur.close()
		conn.close()
	except MySQLdb.Error, e:
		print 'Mysql error %d:%s' %(e.args[0], e.args[1])

def update_db_clawertask(uri):
	try:
		conn = MySQLdb.connect(host='10.100.80.50', user='cacti', passwd='cacti', db='clawer', port=3306)
		cur = conn.cursor()
		for item in uri:
			count = cur.execute("insert into clawer_clawertask(clawer_id, uri, status, add_datetime,  task_generator_id, store, cookie, args) values (%d, '%s', %d, '%s',  %d, %s, %s, %s)" % (7, item, 1, '2016-03-23 16:26:00', 30, 'NULL', 'NULL', 'NULL'))
			conn.commit()
		
		cur.close()
		conn.close()
	except MySQLdb.Error, e:
		print 'Mysql error %d:%s' %(e.args[0], e.args[1])



get_total_dict_from_db()
get_down_dict_from_db()
total_set = set(db_total_list)
down_set = set(db_down_list)
print 'total_set lengths:', len(total_set)
print 'down_set lengths:', len(down_set)
diff_set = total_set - down_set
print 'diff_set lengths:', len(diff_set)

uri = []
with open('all_data.txt', 'r') as f:
	for line in f.readlines():
		if line.split(',')[-1].strip() not in diff_set:
			info = [item.strip().decode('utf8') for item in line.strip().split(',')]
			uri.append(u'enterprise://%s/%s/%s' % tuple(info))

update_db_clawertask()
add_db_clawertask([u'enterprise://广东/深圳市前海美丽神州基金管理有限公司/440301111798558/'])



