#!/usr/bin/env python
#!encoding=utf-8
import os
import sys
import raven
import gzip
import random
import time
import datetime
import stat

import logging
import Queue
import threading
import multiprocessing
import settings
import json
import requests
from crawler import CrawlerUtils

max_crawl_time = 0
yesterday = (datetime.datetime.now() - datetime.timedelta(1)).strftime('%Y%m%d')


def get_json(url):
	pass


def get_pdf(save_path, list_dict):

	reqst = requests.Session()
	reqst.headers.update(
			{'Accept': 'text/html, application/xhtml+xml, */*',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})

	pdf_restore_dir = '%s/%s/%s/%s' % (settings.pdf_restore_dir, save_path[:4],save_path[4:6],save_path[6:])
	if not os.path.exists(pdf_restore_dir):
		CrawlerUtils.make_dir(pdf_restore_dir)

	for item in list_dict:
		pdf_url = item['pdf_url']
		count = 0
		while count <10:
			resp = reqst.get(pdf_url)
			if resp.status_code == 200 and resp.content:
				with open(os.path.join(pdf_restore_dir, pdf_url.rsplit('/')[-1]), 'wb') as f:
					f.write(resp.content)
				break
			else:
				count += 1
				if count == 10:
					print '%s,get-error' % pdf_url
				continue

		# resp = reqst.get(pdf_url, stream = True)
		# if resp.status_code == 200:
		# 	print resp.headers
		# 	with open(os.path.join(pdf_restore_dir, pdf_url.rsplit('/')[-1]), 'wb') as f:
		# 		for chunk in resp.iter_content(chunk_size=1024):
		# 			if chunk:
		# 				f.write(chunk)
		# 				f.flush()
		# else:
		# 	print '%s,get-error' % pdf_url


if __name__ == '__main__':

	max_crawl_time = int(sys.argv[1])
	if len(sys.argv) >= 3 and sys.argv[2] == 'all':
		pass
	else:
		if len(sys.argv) >= 3:
			need_json_file = sys.argv[2:]
		else:
			need_json_file = [yesterday]

		for json_file_item in need_json_file:
			abs_json_path = os.path.join(settings.json_list_dir, json_file_item) + '.json'
			if not os.path.exists(abs_json_path):
				print '-----------error------------'
			else:
				f = open(abs_json_path, 'r')
				for line in f.readlines():
					# print type(json.loads(line)['list'])
					process = multiprocessing.Process(target=get_pdf, args=( json_file_item, json.loads(line)['list']))
					process.daemon = True
					process.start()
					process.join(max_crawl_time)
					print 'child process exit'
				f.close()