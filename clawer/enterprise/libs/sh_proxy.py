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

proxy_url = 'http://proxy.ipcn.org/country/'

set_path = '/tmp/proxies/proxies_2.pik'


reqst = requests.Session()
reqst.headers.update(
			{'Accept': 'text/html, application/xhtml+xml, */*',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})

http_list = []
https_list = []

def test_OK(http):
	proxies = {'http':'http://'+http,'https':'https://'+http}
	try:
		resp = reqst.get('http://lwons.com/wx',timeout=5, proxies=proxies)
		if resp.status_code == 200:
			return True
		return False
	except:
		return False




resp = reqst.get(proxy_url, timeout=10)
table = BeautifulSoup(resp.content).find_all('table', attrs={'border':'1', 'size':'85%'})[-1]
# print table
tds = [td.get_text().strip() for td in table.find_all('td')[:30]]
# print tds
for td in tds:
	if test_OK(td):
		http_list.append('http://'+td)




# timestamp = str(int(time.time()))
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

