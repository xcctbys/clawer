#!/usr/bin/env python
#coding:utf8

import json
import os, os.path
# from bs4 import BeautifulSoup
# import requests
import gzip
import MySQLdb

# import settings

json_url = r'/data/clawer_result/7/2016/02/29/'
abs_json_path = './abs_json_path/'
success_file_path = './success_file_path/'
fail_file_path = './fail_file_path/'
one_json_file = './one_json_file.json'
success_json_file = './success_json_file.json'
fail_json_file = './fail_json_file.json'
trans_dict = dict(
                [('10',u'总局'),
                ('11',u'北京'),
                ('12',u'天津'),
                ('13',u'河北'),
                ('14',u'山西'),
                ('15',u'内蒙古'),
                ('21',u'辽宁'),
                ('22',u'吉林'),
                ('23',u'黑龙江'),
                ('31',u'上海'),
                ('32',u'江苏'),
                ('33',u'浙江'),
                ('34',u'安徽'),
                ('35',u'福建'),
                ('36',u'江西'),
                ('37',u'山东'),
                ('41',u'河南'),
                ('42',u'湖北'),
                ('43',u'湖南'),
                ('44',u'广东'),
                ('45',u'广西'),
                ('46',u'海南'),
                ('50',u'重庆'),
                ('51',u'四川'),
                ('52',u'贵州'),
                ('53',u'云南'),
                ('54',u'西藏'),
                ('61',u'陕西'),
                ('62',u'甘肃'),
                ('63',u'青海'),
                ('64',u'宁夏'),
                ('65',u'新疆'),
                ('71',u'台湾'),
                ('81',u'香港'),
                ('82',u'澳门'),
                ('91',u'总局')])

db_total_dict = dict([('10',set()),
                ('11',set()),
                ('12',set()),
                ('13',set()),
                ('14',set()),
                ('15',set()),
                ('21',set()),
                ('22',set()),
                ('23',set()),
                ('31',set()),
                ('32',set()),
                ('33',set()),
                ('34',set()),
                ('35',set()),
                ('36',set()),
                ('37',set()),
                ('41',set()),
                ('42',set()),
                ('43',set()),
                ('44',set()),
                ('45',set()),
                ('46',set()),
                ('50',set()),
                ('51',set()),
                ('52',set()),
                ('53',set()),
                ('54',set()),
                ('61',set()),
                ('62',set()),
                ('63',set()),
                ('64',set()),
                ('65',set()),
                ('71',set()),
                ('81',set()),
                ('82',set()),
                ('91',set())])

success_dict = dict([('10',set()),
                ('11',set()),
                ('12',set()),
                ('13',set()),
                ('14',set()),
                ('15',set()),
                ('21',set()),
                ('22',set()),
                ('23',set()),
                ('31',set()),
                ('32',set()),
                ('33',set()),
                ('34',set()),
                ('35',set()),
                ('36',set()),
                ('37',set()),
                ('41',set()),
                ('42',set()),
                ('43',set()),
                ('44',set()),
                ('45',set()),
                ('46',set()),
                ('50',set()),
                ('51',set()),
                ('52',set()),
                ('53',set()),
                ('54',set()),
                ('61',set()),
                ('62',set()),
                ('63',set()),
                ('64',set()),
                ('65',set()),
                ('71',set()),
                ('81',set()),
                ('82',set()),
                ('91',set())])

fail_dict = dict([('10',set()),
                ('11',set()),
                ('12',set()),
                ('13',set()),
                ('14',set()),
                ('15',set()),
                ('21',set()),
                ('22',set()),
                ('23',set()),
                ('31',set()),
                ('32',set()),
                ('33',set()),
                ('34',set()),
                ('35',set()),
                ('36',set()),
                ('37',set()),
                ('41',set()),
                ('42',set()),
                ('43',set()),
                ('44',set()),
                ('45',set()),
                ('46',set()),
                ('50',set()),
                ('51',set()),
                ('52',set()),
                ('53',set()),
                ('54',set()),
                ('61',set()),
                ('62',set()),
                ('63',set()),
                ('64',set()),
                ('65',set()),
                ('71',set()),
                ('81',set()),
                ('82',set()),
                ('91',set())])

db_down_dict = dict([('10',set()),
                ('11',set()),
                ('12',set()),
                ('13',set()),
                ('14',set()),
                ('15',set()),
                ('21',set()),
                ('22',set()),
                ('23',set()),
                ('31',set()),
                ('32',set()),
                ('33',set()),
                ('34',set()),
                ('35',set()),
                ('36',set()),
                ('37',set()),
                ('41',set()),
                ('42',set()),
                ('43',set()),
                ('44',set()),
                ('45',set()),
                ('46',set()),
                ('50',set()),
                ('51',set()),
                ('52',set()),
                ('53',set()),
                ('54',set()),
                ('61',set()),
                ('62',set()),
                ('63',set()),
                ('64',set()),
                ('65',set()),
                ('71',set()),
                ('81',set()),
                ('82',set()),
                ('91',set())])


# reqst = requests.Session()
# reqst.headers.update({'Accept': 'text/html, application/xhtml+xml, */*',
# 			'Accept-Encoding': 'gzip, deflate',
# 			'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
# 			'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})

def dowload_json_by_days(url):
	# resp = None
	# # try:
	# resp = reqst.get(url)
	# for item in BeautifulSoup(resp.content).find_all('a')[1:]:
	# 	resp_gzip = reqst.get(''.join([url,item.get_text()]))
	# 	with open(abs_json_path+item.get_text(), 'wb') as f:
	# 		f.write(resp_gzip.content)
	# 	g = gzip.GzipFile(mode='rb', fileobj=open(abs_json_path+item.get_text(), 'rb'))
	# 	open(one_json_file, 'wb+').write(g.read())
		# print resp.status_code
	# except:
	# 	print 'error-get-reqst-%s' % json_url
        for item in os.listdir(url):
                g = gzip.GzipFile(mode='rb', fileobj=open(os.path.join(url, item), 'rb'))
                open(one_json_file, 'wb+').write(g.read())


def dump_json_to_success_or_fail_file(abs_json_path, success_file_path, fail_file_path):
	success_file = open(success_file_path, 'w+')
	fail_file = open(fail_file_path, 'w+')
	with open(abs_json_path, 'rb') as f:
		for line in f.readlines():
			one_enter_dict = json.loads(line)
			for key, value in one_enter_dict.items():
				if key.isdigit():
					if one_enter_dict[key]:
						success_file.write(line)
						success_dict[key[:2]].add(key)
					else:
						fail_file.write(line)
						fail_dict[key[:2]].add(key)
	success_file.close()
	fail_file.close()
	pass

def get_total_dict_from_db():
	try:
		conn = MySQLdb.connect(host='10.100.80.50', user='cacti', passwd='cacti', db='clawer', port=3306)
		cur = conn.cursor()
		count = cur.execute('select register_no from enterprise_enterprise')
		results = cur.fetchall()
		for result in results:
			# print result
			if result[0]:
				db_total_dict[result[0][:2]].add(result[0])
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
			# print result
			if result[0]:
				db_down_dict[result[0][:2]].add(result[0])
		cur.close()
		conn.close()
	except MySQLdb.Error, e:
		print 'Mysql error %d:%s' %(e.args[0], e.args[1])

def alanysis_data():
	for key, value in db_total_dict.items():
		# print trans_dict[key], '\t', key, '\t', len(db_total_dict[key]), '\t', len(success_dict[key]), '\t', len(db_down_dict[key])
                print '%s     %s     %s     %s     %s     %s     %s    %s' %(trans_dict[key], key, len(success_dict[key]), len(fail_dict[key], \
                                                                        len(success_dict[key])-len(fail_dict[key]), len(db_down_dict[key]), \
                                                                        len( (db_down_dict[key] & success_dict[key]) ), \
                                                                        len( (db_down_dict[key] & (success_dict[key] | fail_dict[key])) ))

if __name__ == '__main__':
	dowload_json_by_days(json_url)
	dump_json_to_success_or_fail_file(one_json_file, success_json_file, fail_json_file)
	get_down_dict_from_db()
	get_total_dict_from_db()
	alanysis_data()
	print success_dict
	print fail_dict
