#!/usr/bin/python
#coding:utf8
import sys
import MySQLdb

db_total_list = []
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
		count = cur.execute('delete * from clawer_clawertask where clawer_id=7 and (status=1 or status=2)')
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



