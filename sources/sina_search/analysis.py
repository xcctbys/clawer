#coding=utf-8
"""sina search analysis

"""

import json
import re
import sys
import logging
import unittest
import requests
import time
import os
reload(sys)
sys.setdefaultencoding('utf-8')
from bs4 import BeautifulSoup

def url_read():
    textpath = r"7_1url.txt"
    text = open(textpath)
    arr = []
    for lines in text.readlines():
        lines = lines.replace("\n", "")
        arr.append(lines)
    text.close()
    i = 1
    sName = '7_1content.json'
    f = open(sName, 'w+')

    for url in arr:
        try:
            urltime = re.search(r'\d{8}', url).group(0)
        except:
            i += 1
            continue

        try:
            r = requests.get(url)
        except:
            time.sleep(0.01)

        if int(urltime) > 20121031:
            try:
                soup = BeautifulSoup(r.content.decode('gbk'), "html5lib")
            except:
                soup = BeautifulSoup(r.content, "html5lib")
        else:
            try:
                soup = BeautifulSoup(r.content.decode('gbk'), "html.parser")
            except:
                soup = BeautifulSoup(r.content, "html.parser")

        print u'正在抽取第' + str(i) + u'新闻内容......'

        data = {}
        data["comment_contents"] = {}

        news_title = soup.find('h1', {'id': 'artibodyTitle'})     # 提取文章标题
        if (news_title) == None:
            print u'该网页信息爬取失败！'
        if news_title != None:
            news_title = news_title.string

        news_time = soup.find('span', {'id': 'pub_date'})     # 提取文章时间
        if news_time != None:
            news_time = news_time.string   

        media_name = soup.find('span', {'id': 'media_name'})        # 提取媒体源
        if media_name != None:
            if media_name.a == None:
                media_name = soup.find('span', {'id': 'media_name'}).string
            else:
                media_name = media_name.a.string
            
        keywords = soup.find('p', {'class': 'art_keywords'})        # 提取关键字
        keyword =''
        if keywords != None:
            keywords = keywords.find_all('a')
            for a in keywords:
                keyword = keyword + a.string + ' '

        news_articles = soup.find('div', {'id': 'artibody'})      # 提取正文内容
        p_content = ''
        if news_articles != None:
            news_articles = news_articles.find_all('p')
            for p in news_articles:
                if p.string == None:
                    span = soup.find('p')
                    for span in p:
                        p_content = p_content + str(span.string)
                else:
                    p_content = p_content + p.string

        if int(urltime) < 20050630:
            i += 1
            continue
            
        try:    
            newsId = re.search(r'\d{12}', url).group(0)[4:12]
        except:
            newsId = re.search(r'\d{11}', url)
            if newsId == None:
                continue
            newsId = re.search(r'\d{11}', url).group(0)[4:11]
            
        print u'正在抽取第' + str(i) + u'评论内容......'
        try:
            jscontent = requests.get('http://comment5.news.sina.com.cn/page/info?format=js&channel=cj&newsid=31-1-' + str(newsId) + '&group=&compress=1&ie=gbk&oe=gbk&page=1&page_size=100&jsvar=requestId').content
        except:
            time.sleep(0.01)

        jscontent = jscontent.replace('var requestId=', '')
        js_dict = json.loads(jscontent)
        js_data = js_dict.get('result')
        js_count = js_data.get('count')
        
        try:
            comment_show = js_count.get('show')
            comment_total = js_count.get('total')
        except:
            comment_show = 0
            comment_total = 0
        print comment_show
        print comment_total
        k = 1
        for j in range(1, ((comment_show-1)/100)+2):
            try:
                jscontent = requests.get('http://comment5.news.sina.com.cn/page/info?format=js&channel=cj&newsid=31-1-' + str(newsId) + '&group=&compress=1&ie=gbk&oe=gbk&page=' + str(j) + '&page_size=100&jsvar=requestId').content
            except:
                time.sleep(0.01)

            jscontent = jscontent.replace('var requestId=', '')
            js_dict = json.loads(jscontent)
            js_data = js_dict.get('result')
            cmntlist = js_data.get('cmntlist')
            try:
                for each in cmntlist:
                    comment_content = each.get('content')
#                    print comment_content
                    data["comment_contents"]["content_" + str(k)] = comment_content
                    k += 1
            except:
                time.sleep(0.01)
        
        
        data["title"] = news_title
        data["time"] = news_time
        data["media"] = media_name
        data["keyword"] = keyword
        data["arti_content"] = re.sub('<![^>]*>', '', p_content).strip()
        data["comment_show"] = comment_show
        data["comment_total"] = comment_total
        
        jsonStr = json.dumps(data)
        try:
#            print jsonStr
            f.write(jsonStr)
            f.write('\n')
        except:
            continue
        i+= 1
    f.close





#调用
#sina_search_analysis()
url_read()