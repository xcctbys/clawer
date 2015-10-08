#encoding=utf-8
"""sina search analysis

"""

import json
import re
import sys
import logging
import unittest
import requests
import os
reload(sys)
sys.setdefaultencoding('utf-8')
from bs4 import BeautifulSoup

def url_read():
    textpath=r"1_1url.txt"
    text=open(textpath)
    arr=[]
    for lines in text.readlines():
        lines=lines.replace("\n","")
        arr.append(lines)
    text.close()
    i = 1
    sName = '1_1content.json'
    f = open(sName,'w+')
    for url in arr:
        urltime = re.search(r'\d{8}',url).group(0)
        r = requests.get(url)
        if int(urltime) > 20121031:
            soup = BeautifulSoup(r.content,"html5lib")
        else:
            soup = BeautifulSoup(r.content.decode('gbk'), "html.parser")
        
        print u'正在抽取第' + str(i) + u'新闻内容......'
        
        news_title = soup.find('h1',{'id':'artibodyTitle'})     #提取文章标题
        if (news_title) == None:
            print u'该网页信息爬取失败！'
        if news_title != None:
            news_title = news_title.string

        news_time = soup.find('span',{'id':'pub_date'})     #提取文章时间
        if news_time != None:
            news_time = news_time.string   

        media_name = soup.find('span',{'id':'media_name'})        #提取媒体源
        if media_name != None:
            if media_name.a == None:
                media_name = soup.find('span',{'id':'media_name'}).string
            else:
                media_name = media_name.a.string
            

        keywords = soup.find('p',{'class':'art_keywords'})        #提取关键字
        keyword =''
        if keywords != None:
            keywords = keywords.find_all('a')
            for a in keywords:
                keyword = keyword + a.string + ' '

        news_articles = soup.find('div',{'id':'artibody'})      #提取正文内容
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
        data = {}
        data["title"] = news_title
        data["time"] = news_time
        data["media"] = media_name
        data["keyword"] = keyword
        data["arti_content"] = re.sub('<!--[^>]*-->','',p_content).strip()
        
        
        jsonStr = json.dumps(data)
        try:
            f.write(jsonStr)
            f.write('\n')
        except:
            continue
        i+=1
    f.close

    
#调用
#sina_search_analysis()
url_read()