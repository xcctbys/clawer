#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-01-15 10:06:53
# @Author  : yijiaw
# @Link    : http://example.org
# @Version : $Id$

import time
import datetime


def trans_time(s):
    # s = ['2014年6月24日','2015-05-18']
    try:
        a = time.strptime(s, '%Y年%m月%d日')
        time1 = datetime.datetime(*a[:6])
        return time1
    except:
        try:
            b = time.strptime(s, '%Y-%m-%d')
            time2 = datetime.datetime(*b[:6])
            return time2
        except:
            return None


if __name__ == '__main__':
    trans_time('2014年6月24日')
    trans_time('2015-05-18')
