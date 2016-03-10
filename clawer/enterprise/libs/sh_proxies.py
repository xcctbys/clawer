#!/usr/bin python
#coding:utf8

import requests
from bs4 import BeautifulSoup
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import os
import os.path
import time
import datetime
import cPickle as pickle

xici_url = 'http://www.xicidaili.com/'
sixsix_url = 'http://www.66ip.cn/areaindex_'

set_path = '/tmp/proxies/proxies.pik'
#set_path = './proxies/proxies.pik'

reqst = requests.Session()
reqst.headers.update(
			{'Accept': 'text/html, application/xhtml+xml, */*',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})

http_list = []
https_list = []

def test_OK(http):
	proxies = {'http':http,'https':http}
	try:
		resp = reqst.get('http://www.baidu.com',timeout=5, proxies=proxies)
		if resp.status_code == 200:
			return True
		return False
	except:
		return False


def get_list_from_xici(trs):
	for tr in trs[2:]:
		tds = [td.get_text() for td in tr.find_all('td')]
		if tds[5] == 'HTTP':
			http =  "%s://%s:%s" % (tds[5].lower(),tds[1],tds[2])
			# print http
			if test_OK(http):
				http_list.append(http)
		elif tds[5] == 'HTTPS':
			https = "%s://%s:%s" % (tds[5].lower(),tds[1],tds[2])
			# print https
			if test_OK(https):
				http_list.append(https)


resp = reqst.get(xici_url, timeout=10)
trs = BeautifulSoup(resp.content).find_all('tr')[:11]
get_list_from_xici(trs)

for i in range(1,33):
	url = sixsix_url+str(i)+'/'+'1.html'
	try:
		resp = reqst.get(url, timeout=5)
	except:
		continue
	table = BeautifulSoup(resp.content).find_all('table', attrs={'width':'100%', 'border':"2px", 'cellspacing':"0px", 'bordercolor':"#6699ff"})[0]
	trs = table.find_all('tr')[1:4]
	for tr in trs:
		tds = [td.get_text() for td in tr.find_all('td')]
		http = "%s://%s:%s" % ('http',tds[0],tds[1])
		print http
		if test_OK(http):
			http_list.append(http)


timestamp = str(int(time.time()))
# print timestamp
print http_list
# print https_list

if not os.path.exists(os.path.dirname(set_path)):
	os.makedirs(os.path.dirname(set_path))
if http_list:
	f = file(set_path, 'wb')
	pickle.dump(http_list, f, True)
	f.close()

# f = file(os.path.join(os.getcwd(), 'proxies/'+ timestamp), 'rb')
# http_list = pickle.load(f)
# print http_list
# f.close()

