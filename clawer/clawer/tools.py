#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-01-15 10:06:53
# @Author  : yijiaw
# @Link    : http://example.org
# @Version : $Id$

import os
import time
import datetime

def trans_time(self):
	# s = ['2014年6月24日','2015-05-18']
	# for i in range(2):
	try:
		a = time.strptime(self,'%Y年%m月%d日')
		time1 = datetime.datetime(*a[:6])
		return time1
	except:
		b = time.strptime(self,'%Y-%m-%d')
		time2 = datetime.datetime(*b[:6])
		return time2


if __name__ == '__main__':
	trans_time()
